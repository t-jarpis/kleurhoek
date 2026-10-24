import { Inject, Injectable } from "@nestjs/common";
import { and, asc, eq, inArray } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "../identity/audit.service";
import { LocalizationService } from "../localization/localization.service";
import { materialProducts, partners, products } from "./shop.schema";

export class ShopError extends Error {
  constructor(readonly code: "not_found" | "invalid", message: string) { super(message); }
}

const SETTING_KEY = /^[a-zA-Z][a-zA-Z0-9]{0,31}$/;
const SETTING_VALUE = /^[A-Za-z0-9_.-]{0,64}$/;
const SLUG = /^[a-z0-9-]{2,64}$/;

/** Zet {url}, {subId} en {sleutel} uit de instellingen in het sjabloon. Null als er iets ontbreekt. */
export function buildLink(template: string, settings: Record<string, string>, productUrl: string, subId: string): string | null {
  let missing = false;
  const out = template.replace(/\{([a-zA-Z]+)\}/g, (_, key: string) => {
    // Begint het sjabloon met {url} (zoals Amazon: "{url}?tag={tag}"), dan gaat de URL er letterlijk in;
    // als parameter van een netwerklink (bol, Awin, Daisycon) gaat hij gecodeerd mee.
    if (key === "url") return template.startsWith("{url}") ? productUrl : encodeURIComponent(productUrl);
    if (key === "subId") return encodeURIComponent(subId);
    const v = settings[key];
    if (!v) { missing = true; return ""; }
    return encodeURIComponent(v);
  });
  if (missing) return null;
  // "{url}?tag=…" op een productlink die zelf al een vraagteken heeft (Amazon: ?th=1): de parameters van
  // het sjabloon netjes toevoegen (of vervangen) in plaats van een tweede "?" achter de URL te plakken.
  if (template.startsWith("{url}?")) {
    try {
      const u = new URL(productUrl);
      for (const [k, v] of new URLSearchParams(out.slice(productUrl.length + 1))) u.searchParams.set(k, v);
      return u.protocol === "https:" ? u.href : null;
    } catch {
      return null;
    }
  }
  try {
    const u = new URL(out);
    return u.protocol === "https:" ? u.href : null;
  } catch {
    return null;
  }
}

/** Een sjabloon moet {url} bevatten en naar https leiden (of met {url} zelf beginnen). */
function validateTemplate(template: string): string {
  const t = template.trim();
  if (!t.includes("{url}")) throw new ShopError("invalid", "Het sjabloon moet {url} bevatten");
  if (!t.startsWith("{url}") && !t.startsWith("https://")) throw new ShopError("invalid", "Het sjabloon moet met https:// of {url} beginnen");
  if (t.length > 500) throw new ShopError("invalid", "Het sjabloon is te lang");
  return t;
}

/** Alleen https-pagina's, en bij partners met een lijst alleen op hun eigen domeinen. */
export function checkProductUrl(url: string, allowedHosts: string[]): string | null {
  try {
    const u = new URL(url);
    if (u.protocol !== "https:" || u.username || u.password) return "Alleen https-adressen";
    if (allowedHosts.length && !allowedHosts.includes(u.hostname)) return `Dit adres hoort niet bij de partner (${allowedHosts.join(", ")})`;
    return null;
  } catch {
    return "Geen geldig adres";
  }
}

/** Korte deellinks van Amazon (app, deelknop): die volgen we tot de echte productpagina. */
const AMAZON_SHORT = new Set(["amzn.eu", "amzn.to", "a.co", "amzn.com"]);
const AMAZON_HOST = /^(?:www\.)?(amazon\.(?:nl|de|fr|be|com\.be|es|it|co\.uk|com))$/;
const ASIN = /\/(?:dp|gp\/product|gp\/aw\/d|d)\/([A-Z0-9]{10})(?:[/?]|$)/i;

/**
 * Productlink netjes maken vóór we hem opslaan: korte Amazon-links volgen, en Amazon terugbrengen tot
 * https://www.amazon.<land>/dp/<ASIN> (zonder verwijzingen of tags van anderen); bol.com met www.
 * `follow` haalt de doorverwijzing op (in tests nagebootst). Onbekende winkels blijven ongewijzigd.
 */
export async function normalizeProductUrl(raw: string, follow: (url: string) => Promise<string | null> = followRedirect): Promise<string> {
  let url = raw.trim();
  for (let i = 0; i < 4; i++) {
    let host: string;
    try { host = new URL(url).hostname.toLowerCase(); } catch { return raw.trim(); }
    if (!AMAZON_SHORT.has(host)) break;
    const next = await follow(url);
    if (!next) return raw.trim();
    url = next;
  }
  try {
    const u = new URL(url);
    const amazon = AMAZON_HOST.exec(u.hostname.toLowerCase());
    if (amazon) {
      const asin = ASIN.exec(u.pathname + "/")?.[1];
      return asin ? `https://www.${amazon[1]}/dp/${asin.toUpperCase()}` : `https://www.${amazon[1]}${u.pathname}`;
    }
    if (u.hostname.toLowerCase() === "bol.com") u.hostname = "www.bol.com";
    return u.href;
  } catch {
    return raw.trim();
  }
}

/** Eén stap van een doorverwijzing (alleen https, korte time-out). */
async function followRedirect(url: string): Promise<string | null> {
  try {
    const res = await fetch(url, { method: "GET", redirect: "manual", signal: AbortSignal.timeout(5000), headers: { "user-agent": "Mozilla/5.0 (Kleurhoek admin; productlink)" } });
    const loc = res.headers.get("location");
    if (!loc) return null;
    const next = new URL(loc, url);
    return next.protocol === "https:" ? next.href : null;
  } catch {
    return null;
  }
}

export interface ProductView {
  slug: string; partner: string; url: string; ean: string | null; priceHint: string | null; enabled: boolean;
  markets: string[]; name: string | null; note: string | null; materials: string[]; rank: number;
}

/**
 * Domein Winkel (fase 1: affiliate). Kent partners, producten en welk product bij welk materiaal
 * hoort. Bouwt doorverwijzingen alleen uit opgeslagen gegevens: nooit uit invoer van bezoekers.
 */
@Injectable()
export class ShopService {
  constructor(
    @Inject(DB) private readonly db: Database,
    @Inject(ENV) private readonly env: Env,
    private readonly i18n: LocalizationService,
    private readonly audit: AuditService,
  ) {}

  private get tenant() { return this.env.TENANT_ID; }

  async partners() {
    return withTenant(this.db, this.tenant, (tx) => tx.select({
      slug: partners.slug, name: partners.name, enabled: partners.enabled, linkTemplate: partners.linkTemplate,
      settings: partners.settings, allowedHosts: partners.allowedHosts, updatedBy: partners.updatedBy, updatedAt: partners.updatedAt,
    }).from(partners).orderBy(asc(partners.slug)));
  }

  /** Een eigen partner toevoegen, bijvoorbeeld een winkel via Daisycon, Awin of TradeTracker. */
  async createPartner(actor: string, input: { slug: string; name: string; linkTemplate: string; allowedHosts: string[] }) {
    if (!/^[a-z0-9-]{2,32}$/.test(input.slug)) throw new ShopError("invalid", "Gebruik voor de code kleine letters, cijfers en streepjes");
    validateTemplate(input.linkTemplate);
    for (const h of input.allowedHosts) if (!/^[a-z0-9.-]+\.[a-z]{2,}$/.test(h)) throw new ShopError("invalid", `Ongeldig domein: ${h}`);
    if (!input.allowedHosts.length) throw new ShopError("invalid", "Geef minstens één domein van de winkel op");
    return withTenant(this.db, this.tenant, async (tx) => {
      const [exists] = await tx.select({ slug: partners.slug }).from(partners).where(eq(partners.slug, input.slug)).limit(1);
      if (exists) throw new ShopError("invalid", "Die code bestaat al");
      await tx.insert(partners).values({ tenantId: this.tenant, slug: input.slug, name: input.name, enabled: false, linkTemplate: input.linkTemplate.trim(), settings: {}, allowedHosts: input.allowedHosts, updatedBy: actor });
      await this.audit.record(tx, this.tenant, { actor, action: "shop.partner.created", subject: `partner:${input.slug}`, after: input });
      return input.slug;
    });
  }

  async updatePartner(actor: string, slug: string, change: { enabled?: boolean | undefined; linkTemplate?: string | undefined; settings?: Record<string, string> | undefined }) {
    if (change.linkTemplate !== undefined) change.linkTemplate = validateTemplate(change.linkTemplate);
    if (change.settings) {
      for (const [k, v] of Object.entries(change.settings)) {
        if (!SETTING_KEY.test(k) || !SETTING_VALUE.test(v)) throw new ShopError("invalid", `Ongeldige instelling: ${k}`);
      }
    }
    return withTenant(this.db, this.tenant, async (tx) => {
      const [before] = await tx.select().from(partners).where(eq(partners.slug, slug)).limit(1);
      if (!before) throw new ShopError("not_found", "Onbekende partner");
      const next = {
        enabled: change.enabled ?? before.enabled,
        linkTemplate: change.linkTemplate ?? before.linkTemplate,
        settings: change.settings ?? before.settings,
      };
      if (next.enabled && buildLink(next.linkTemplate, next.settings, "https://example.com/p", "test") === null) {
        throw new ShopError("invalid", "Vul eerst alle instellingen in die het sjabloon gebruikt");
      }
      await tx.update(partners).set({ ...next, updatedBy: actor, updatedAt: new Date() }).where(eq(partners.slug, slug));
      await this.audit.record(tx, this.tenant, {
        actor, action: "shop.partner.updated", subject: `partner:${slug}`,
        before: { enabled: before.enabled, linkTemplate: before.linkTemplate, settings: before.settings },
        after: next,
      });
      return { slug, ...next };
    });
  }

  async products(language: string): Promise<ProductView[]> {
    const [rows, links] = await withTenant(this.db, this.tenant, async (tx) => [
      await tx.select().from(products).orderBy(asc(products.slug)),
      await tx.select().from(materialProducts).orderBy(asc(materialProducts.rank)),
    ] as const);
    const names = await this.i18n.translate(this.tenant, "product", language, rows.map((r) => r.slug));
    return rows.map((r) => ({
      slug: r.slug, partner: r.partnerSlug, url: r.url, ean: r.ean, priceHint: r.priceHint, enabled: r.enabled, markets: r.markets,
      name: names.get(r.slug)?.name ?? null, note: names.get(r.slug)?.note ?? null,
      materials: links.filter((l) => l.productSlug === r.slug).map((l) => l.materialSlug),
      rank: links.find((l) => l.productSlug === r.slug)?.rank ?? 0,
    }));
  }

  /** Product aanmaken of bijwerken, inclusief naam (in de taal van de markt) en gekoppelde materialen. */
  async saveProduct(actor: string, language: string, input: {
    slug: string; partner: string; url: string; ean?: string | null | undefined; priceHint?: string | null | undefined;
    enabled: boolean; markets: string[]; name: string; note?: string | null | undefined; materials: string[];
    /** Voorkeur als er meer producten bij een materiaal horen: laagste eerst. */
    rank?: number | undefined;
  }) {
    if (!SLUG.test(input.slug)) throw new ShopError("invalid", "Gebruik kleine letters, cijfers en streepjes voor de code");
    input = { ...input, url: await normalizeProductUrl(input.url) };
    const result = await withTenant(this.db, this.tenant, async (tx) => {
      const [partner] = await tx.select().from(partners).where(eq(partners.slug, input.partner)).limit(1);
      if (!partner) throw new ShopError("invalid", "Onbekende partner");
      const problem = checkProductUrl(input.url, partner.allowedHosts);
      if (problem) {
        // Hoort de link bij een andere partner? Zeg dan welke.
        const all = await tx.select({ name: partners.name, hosts: partners.allowedHosts }).from(partners);
        const host = (() => { try { return new URL(input.url).hostname; } catch { return ""; } })();
        const other = all.find((p) => p.hosts.includes(host));
        throw new ShopError("invalid", other ? `Dit is een link van ${other.name}: kies die partner` : problem);
      }
      const [before] = await tx.select().from(products).where(eq(products.slug, input.slug)).limit(1);
      const values = { partnerSlug: input.partner, url: input.url, ean: input.ean ?? null, priceHint: input.priceHint ?? null, enabled: input.enabled, markets: input.markets };
      if (before) await tx.update(products).set({ ...values, updatedAt: new Date() }).where(eq(products.slug, input.slug));
      else await tx.insert(products).values({ tenantId: this.tenant, slug: input.slug, ...values });
      await tx.delete(materialProducts).where(eq(materialProducts.productSlug, input.slug));
      if (input.materials.length) {
        await tx.insert(materialProducts).values(input.materials.map((m) => ({ tenantId: this.tenant, materialSlug: m, productSlug: input.slug, rank: input.rank ?? 0 })));
      }
      await this.audit.record(tx, this.tenant, { actor, action: before ? "shop.product.updated" : "shop.product.created", subject: `product:${input.slug}`, before: before ?? null, after: { ...values, materials: input.materials } });
      return input.slug;
    });
    await this.i18n.save(this.tenant, "product", input.slug, language, { name: input.name, note: input.note ?? null });
    return result;
  }

  /**
   * Per materiaal het product dat we tonen: ingeschakeld, voor deze markt, bij een partner die aan
   * staat. Materialen zonder product ontbreken in de map.
   */
  async forMaterials(market: string, language: string, materialSlugs: string[]) {
    if (!materialSlugs.length) return new Map<string, { slug: string; name: string; note: string | null; priceHint: string | null; partner: string }>();
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({
      material: materialProducts.materialSlug, slug: products.slug, priceHint: products.priceHint, partner: partners.name, markets: products.markets,
    }).from(materialProducts)
      .innerJoin(products, and(eq(products.slug, materialProducts.productSlug), eq(products.tenantId, materialProducts.tenantId)))
      .innerJoin(partners, and(eq(partners.slug, products.partnerSlug), eq(partners.tenantId, products.tenantId)))
      .where(and(inArray(materialProducts.materialSlug, materialSlugs), eq(products.enabled, true), eq(partners.enabled, true)))
      .orderBy(asc(materialProducts.rank), asc(products.slug)));
    const names = await this.i18n.translate(this.tenant, "product", language, [...new Set(rows.map((r) => r.slug))]);
    const out = new Map<string, { slug: string; name: string; note: string | null; priceHint: string | null; partner: string }>();
    for (const r of rows) {
      const name = names.get(r.slug)?.name;
      if (out.has(r.material) || !name || !r.markets.includes(market)) continue;
      out.set(r.material, { slug: r.slug, name, note: names.get(r.slug)?.note ?? null, priceHint: r.priceHint, partner: r.partner });
    }
    return out;
  }

  /**
   * Producten op volgorde van `productSlugs` (bijvoorbeeld bij een thema uit de Bronnengids): alleen
   * ingeschakeld, voor deze markt, bij een partner die aan staat en met een naam in deze taal.
   */
  async forProducts(market: string, language: string, productSlugs: string[]) {
    if (!productSlugs.length) return [];
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({ slug: products.slug, priceHint: products.priceHint, partner: partners.name, markets: products.markets })
      .from(products).innerJoin(partners, and(eq(partners.slug, products.partnerSlug), eq(partners.tenantId, products.tenantId)))
      .where(and(inArray(products.slug, productSlugs), eq(products.enabled, true), eq(partners.enabled, true))));
    const names = await this.i18n.translate(this.tenant, "product", language, rows.map((r) => r.slug));
    return productSlugs.flatMap((slug) => {
      const r = rows.find((x) => x.slug === slug), name = names.get(slug)?.name;
      return r && name && r.markets.includes(market) ? [{ slug, name, note: names.get(slug)?.note ?? null, priceHint: r.priceHint, partner: r.partner }] : [];
    });
  }

  /** De doorverwijzing voor een product, of null als het (in deze markt) niet getoond mag worden. */
  async link(market: string, productSlug: string, subId: string): Promise<string | null> {
    const [row] = await withTenant(this.db, this.tenant, (tx) => tx.select({
      url: products.url, markets: products.markets, template: partners.linkTemplate, settings: partners.settings, allowedHosts: partners.allowedHosts,
    }).from(products)
      .innerJoin(partners, and(eq(partners.slug, products.partnerSlug), eq(partners.tenantId, products.tenantId)))
      .where(and(eq(products.slug, productSlug), eq(products.enabled, true), eq(partners.enabled, true))).limit(1));
    if (!row || !row.markets.includes(market)) return null;
    if (checkProductUrl(row.url, row.allowedHosts)) return null;
    return buildLink(row.template, row.settings, row.url, subId);
  }
}
