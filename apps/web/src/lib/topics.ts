import type { Messages } from "@/i18n/nl";
import { KIND_GROUP, type PlateItem, type Taxonomy } from "./types";

/**
 * Onderwerppagina's (ADR 0055): elke waarde van een filter is ook een eigen pagina met een vast adres, zodat
 * zoekmachines "kleurplaten dieren" of "Ausmalbilder Weihnachten" kunnen vinden. De filters op de voorpagina
 * blijven zoals ze zijn; deze pagina's tonen hetzelfde, maar dan op de server en met een eigen titel en tekst.
 */
export const DIMENSIONS = ["onderwerp", "feestdag", "leeftijd", "soort", "werelddeel"] as const;
export type Dimension = (typeof DIMENSIONS)[number];

export interface Topic { dim: Dimension; slug: string; name: string; color: string | null; count: number; path: string }

const KIND_GROUPS = ["kleurplaat", "knutselen", "leren", "tekenen"] as const;

/** Of een plaat bij een onderwerp hoort. */
export function inTopic(p: PlateItem, dim: Dimension, slug: string): boolean {
  switch (dim) {
    case "onderwerp": return p.category === slug;
    case "feestdag": return p.holiday === slug;
    case "leeftijd": return p.age === slug;
    case "soort": return KIND_GROUP[p.kind] === slug;
    case "werelddeel": return p.world?.continent === slug;
  }
}

/** Naam van een soort ("Kleurplaten", "Knutselen" …) uit de interfaceteksten. */
function kindName(t: Messages, slug: string): string {
  return ({ kleurplaat: t.kindColoring, knutselen: t.kindCrafts, leren: t.kindLearn, tekenen: t.kindDrawing } as Record<string, string>)[slug] ?? slug;
}

/** Alle onderwerpen van een markt met minstens één plaat, per dimensie, in de volgorde van de taxonomie. */
export function topics(plates: PlateItem[], taxonomy: Taxonomy, t: Messages): Record<Dimension, Topic[]> {
  const count = (dim: Dimension, slug: string) => plates.reduce((n, p) => n + (inTopic(p, dim, slug) ? 1 : 0), 0);
  const make = (dim: Dimension, items: { slug: string; name: string; color?: string | null }[]) => items
    .map((i) => ({ dim, slug: i.slug, name: i.name, color: i.color ?? null, count: count(dim, i.slug), path: `/${dim}/${i.slug}` }))
    .filter((x) => x.count > 0);
  return {
    onderwerp: make("onderwerp", taxonomy.categories),
    feestdag: make("feestdag", taxonomy.holidays),
    leeftijd: make("leeftijd", taxonomy.ages),
    soort: make("soort", KIND_GROUPS.map((slug) => ({ slug, name: kindName(t, slug) }))),
    werelddeel: make("werelddeel", taxonomy.continents),
  };
}

/** De kop (H1) van een onderwerppagina in de taal van de markt. */
export function topicTitle(t: Messages, topic: Pick<Topic, "dim" | "slug" | "name">): string {
  if (topic.dim === "soort") return (t.kindH1 as Record<string, string>)[topic.slug] ?? topic.name;
  return t.topicH1[topic.dim](topic.name);
}
