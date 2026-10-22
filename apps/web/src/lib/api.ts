import "server-only";
import { svgInner } from "./svg";
import type { PlateDetail, PlateItem, Season, Taxonomy } from "./types";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

export class NotFound extends Error {}

async function get<T>(path: string, revalidate: number, tags: string[]): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { next: { revalidate, tags }, headers: { accept: "application/json" } });
  if (res.status === 404) throw new NotFound(path);
  if (!res.ok) throw new Error(`API ${res.status} op ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  plates: (market: string) => get<{ count: number; items: PlateItem[] }>(`/v1/markets/${market}/plates`, 300, ["plates", `market:${market}`]).then((r) => r.items),
  plate: (market: string, slug: string) => get<PlateDetail>(`/v1/markets/${market}/plates/${encodeURIComponent(slug)}`, 300, ["plates", `plate:${slug}`]),
  taxonomy: (market: string) => get<Taxonomy>(`/v1/markets/${market}/taxonomy`, 3600, ["taxonomy", `market:${market}`]),
  season: (market: string) => get<Season>(`/v1/markets/${market}/season`, 900, ["season", `market:${market}`]),
  /** De SVG zonder stijlblok, om inline in de pagina te tekenen (de CSS van de site stijlt hem). */
  async plateSvgInner(path: string): Promise<{ inner: string }> {
    const res = await fetch(`${API_URL}${path}`, { next: { revalidate: 31_536_000, tags: ["svg"] } });
    if (!res.ok) throw new NotFound(path);
    return { inner: svgInner(await res.text()) };
  },
};
