/**
 * Koppelingen met Pinterest en Meta (Facebook en Instagram), ADR 0063. Alleen de officiële API's met OAuth: geen
 * wachtwoorden en geen scraping. `fetch` is in te ruilen, zodat de tests niet naar buiten gaan.
 */
export type Fetch = (url: string, init?: RequestInit) => Promise<Response>;
export interface Tokens { access: string; refresh?: string | undefined; expiresAt?: number | undefined; refreshExpiresAt?: number | undefined }
export interface Published { id: string; url: string }

export class ApiProblem extends Error {
  constructor(message: string, readonly status = 0) { super(message); }
}

async function json<T>(res: Response, what: string): Promise<T> {
  const text = await res.text();
  let body: unknown = null;
  try { body = JSON.parse(text); } catch { /* geen JSON */ }
  if (!res.ok) {
    const b = body as { message?: string; error?: { message?: string } } | null;
    throw new ApiProblem(`${what}: ${b?.error?.message ?? b?.message ?? text.slice(0, 200)}`, res.status);
  }
  return body as T;
}

// ---------- Pinterest (API v5) ----------

export const PINTEREST_SCOPES = ["boards:read", "boards:write", "pins:read", "pins:write", "user_accounts:read"];

export class Pinterest {
  constructor(private readonly fetch: Fetch, private readonly appId: string, private readonly secret: string, private readonly base = "https://api.pinterest.com") {}

  authorizeUrl(redirectUri: string, state: string) {
    return `https://www.pinterest.com/oauth/?${new URLSearchParams({ client_id: this.appId, redirect_uri: redirectUri, response_type: "code", scope: PINTEREST_SCOPES.join(","), state })}`;
  }

  private async token(body: Record<string, string>): Promise<Tokens> {
    const res = await this.fetch(`${this.base}/v5/oauth/token`, {
      method: "POST",
      headers: { authorization: `Basic ${Buffer.from(`${this.appId}:${this.secret}`).toString("base64")}`, "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(body).toString(),
    });
    const t = await json<{ access_token: string; refresh_token?: string; expires_in?: number; refresh_token_expires_in?: number }>(res, "Pinterest-token");
    const now = Date.now();
    return { access: t.access_token, refresh: t.refresh_token ?? body.refresh_token, expiresAt: t.expires_in ? now + t.expires_in * 1000 : undefined, refreshExpiresAt: t.refresh_token_expires_in ? now + t.refresh_token_expires_in * 1000 : undefined };
  }

  exchange(code: string, redirectUri: string) { return this.token({ grant_type: "authorization_code", code, redirect_uri: redirectUri }); }
  refresh(t: Tokens) {
    if (!t.refresh) throw new ApiProblem("Pinterest: geen vernieuwingssleutel; koppel opnieuw");
    return this.token({ grant_type: "refresh_token", refresh_token: t.refresh });
  }

  private call<T>(t: Tokens, path: string, init: RequestInit = {}) {
    return this.fetch(`${this.base}${path}`, { ...init, headers: { authorization: `Bearer ${t.access}`, ...(init.body ? { "content-type": "application/json" } : {}) } }).then((r) => json<T>(r, `Pinterest ${path.split("?")[0]}`));
  }

  async account(t: Tokens) { return (await this.call<{ username: string }>(t, "/v5/user_account")).username; }

  /** Het bord met deze naam; bestaat het niet, dan maken we het aan. */
  async board(t: Tokens, name: string, known: Record<string, string>): Promise<string> {
    if (known[name]) return known[name]!;
    let bookmark: string | undefined;
    do {
      const page = await this.call<{ items: { id: string; name: string }[]; bookmark?: string | null }>(t, `/v5/boards?page_size=250${bookmark ? `&bookmark=${encodeURIComponent(bookmark)}` : ""}`);
      const hit = page.items.find((b) => b.name.toLowerCase() === name.toLowerCase());
      if (hit) return hit.id;
      bookmark = page.bookmark ?? undefined;
    } while (bookmark);
    return (await this.call<{ id: string }>(t, "/v5/boards", { method: "POST", body: JSON.stringify({ name, privacy: "PUBLIC" }) })).id;
  }

  async pin(t: Tokens, p: { boardId: string; title: string; description: string; link: string; image: string; alt: string }): Promise<Published> {
    const r = await this.call<{ id: string }>(t, "/v5/pins", {
      method: "POST",
      body: JSON.stringify({ board_id: p.boardId, title: p.title.slice(0, 100), description: p.description.slice(0, 500), link: p.link, alt_text: p.alt.slice(0, 500), media_source: { source_type: "image_url", url: p.image } }),
    });
    return { id: r.id, url: `https://www.pinterest.com/pin/${r.id}/` };
  }
}

// ---------- Meta: Facebook-pagina en Instagram (Graph API) ----------

export const GRAPH_VERSION = "v25.0";
export const META_SCOPES = ["pages_show_list", "pages_manage_posts", "pages_read_engagement", "instagram_basic", "instagram_content_publish", "business_management"];
export interface MetaPage { id: string; name: string; token: string; instagram: { id: string; username: string } | null }

export class Meta {
  constructor(private readonly fetch: Fetch, private readonly appId: string, private readonly secret: string, private readonly graph = `https://graph.facebook.com/${GRAPH_VERSION}`) {}

  authorizeUrl(redirectUri: string, state: string) {
    return `https://www.facebook.com/${GRAPH_VERSION}/dialog/oauth?${new URLSearchParams({ client_id: this.appId, redirect_uri: redirectUri, state, scope: META_SCOPES.join(","), response_type: "code" })}`;
  }

  private get<T>(path: string, params: Record<string, string>) {
    return this.fetch(`${this.graph}${path}?${new URLSearchParams(params)}`).then((r) => json<T>(r, `Meta ${path}`));
  }
  private post<T>(path: string, params: Record<string, string>) {
    return this.fetch(`${this.graph}${path}`, { method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(params).toString() }).then((r) => json<T>(r, `Meta ${path}`));
  }

  /**
   * Code → gebruikerssleutel → langlevende gebruikerssleutel → de pagina's met hun sleutels. Een paginasleutel die
   * van een langlevende gebruikerssleutel komt, verloopt niet; die bewaren we.
   */
  async pages(code: string, redirectUri: string): Promise<MetaPage[]> {
    const short = await this.get<{ access_token: string }>("/oauth/access_token", { client_id: this.appId, client_secret: this.secret, redirect_uri: redirectUri, code });
    const long = await this.get<{ access_token: string }>("/oauth/access_token", { grant_type: "fb_exchange_token", client_id: this.appId, client_secret: this.secret, fb_exchange_token: short.access_token });
    const res = await this.get<{ data: { id: string; name: string; access_token: string; instagram_business_account?: { id: string; username?: string } }[] }>("/me/accounts", { fields: "id,name,access_token,instagram_business_account{id,username}", access_token: long.access_token });
    return res.data.map((p) => ({ id: p.id, name: p.name, token: p.access_token, instagram: p.instagram_business_account ? { id: p.instagram_business_account.id, username: p.instagram_business_account.username ?? p.instagram_business_account.id } : null }));
  }

  /** Foto met tekst op de Facebook-pagina. */
  async facebook(pageId: string, token: string, p: { message: string; image: string }): Promise<Published> {
    const r = await this.post<{ id: string; post_id?: string }>(`/${pageId}/photos`, { url: p.image, message: p.message, published: "true", access_token: token });
    const id = r.post_id ?? r.id;
    return { id, url: `https://www.facebook.com/${id}` };
  }

  /** Instagram: eerst een container met de afbeelding (JPEG), dan publiceren. */
  async instagram(igId: string, token: string, p: { caption: string; image: string }): Promise<Published> {
    const c = await this.post<{ id: string }>(`/${igId}/media`, { image_url: p.image, caption: p.caption, access_token: token });
    for (let i = 0; i < 10; i++) {
      const s = await this.get<{ status_code?: string }>(`/${c.id}`, { fields: "status_code", access_token: token });
      if (!s.status_code || s.status_code === "FINISHED") break;
      if (s.status_code === "ERROR" || s.status_code === "EXPIRED") throw new ApiProblem(`Instagram kon de afbeelding niet verwerken (${s.status_code})`);
      await new Promise((r) => setTimeout(r, 3000));
    }
    const m = await this.post<{ id: string }>(`/${igId}/media_publish`, { creation_id: c.id, access_token: token });
    const link = await this.get<{ permalink?: string }>(`/${m.id}`, { fields: "permalink", access_token: token }).catch(() => ({ permalink: undefined }));
    return { id: m.id, url: link.permalink ?? "https://www.instagram.com/" };
  }
}
