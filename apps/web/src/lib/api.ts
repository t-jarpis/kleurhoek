import "server-only";
import { svgInner } from "./svg";
import type { PlateDetail, PlateItem, Season, Taxonomy, ThemeDetail, ThemeItem } from "./types";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

export class NotFound extends Error {}

async function get<T>(path: string, revalidate: number, tags: string[]): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { next: { revalidate, tags }, headers: { accept: "application/json" } });
  if (res.status === 404) throw new NotFound(path);
  if (!res.ok) throw new Error(`API ${res.status} op ${path}`);
  return res.json() as Promise<T>;
}

/** Elke aanroep geldt voor een organisatie (?org=…): die bepaalt het aanbod en of de winkel aan staat. */
const o = (org: string) => `org=${encodeURIComponent(org)}`;

export const api = {
  plates: (market: string, org: string) => get<{ count: number; items: PlateItem[] }>(`/v1/markets/${market}/plates?${o(org)}`, 300, ["plates", `market:${market}`, `org:${org}`]).then((r) => r.items),
  plate: (market: string, slug: string, org: string) => get<PlateDetail>(`/v1/markets/${market}/plates/${encodeURIComponent(slug)}?${o(org)}`, 300, ["plates", `plate:${slug}`, `org:${org}`]),
  taxonomy: (market: string, org: string) => get<Taxonomy>(`/v1/markets/${market}/taxonomy?${o(org)}`, 3600, ["taxonomy", `market:${market}`, `org:${org}`]),
  season: (market: string, org: string) => get<Season>(`/v1/markets/${market}/season?${o(org)}`, 900, ["season", `market:${market}`, `org:${org}`]),
  themes: (market: string, org: string) => get<{ themes: ThemeItem[] }>(`/v1/markets/${market}/themes?${o(org)}`, 300, ["themes", `market:${market}`, `org:${org}`]).then((r) => r.themes),
  theme: (market: string, slug: string, org: string) => get<ThemeDetail>(`/v1/markets/${market}/themes/${encodeURIComponent(slug)}?${o(org)}`, 300, ["themes", `theme:${slug}`, `org:${org}`]),
  /** De SVG zonder stijlblok, om inline in de pagina te tekenen (de CSS van de site stijlt hem). */
  async plateSvgInner(path: string): Promise<{ inner: string }> {
    const res = await fetch(`${API_URL}${path}`, { next: { revalidate: 31_536_000, tags: ["svg"] } });
    if (!res.ok) throw new NotFound(path);
    return { inner: svgInner(await res.text()) };
  },
};
