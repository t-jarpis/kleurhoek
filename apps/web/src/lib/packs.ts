import { KIND_GROUP, type PlateItem, type Taxonomy } from "./types";

/**
 * Lespakketten (ADR 0059): per onderwerp en leeftijd een kant-en-klare set. Eerst kleurplaten als rustige start,
 * dan werkbladen en spellen (leren), dan iets om te knutselen of te tekenen. Alleen als er genoeg is: minstens
 * vijf platen, waarvan minstens één om te leren of te maken. Alles volgt uit de platen zelf, dus nieuwe platen
 * komen vanzelf in de pakketten.
 */
export interface Pack {
  slug: string;
  category: { slug: string; name: string; color: string };
  age: { slug: string; name: string };
  plates: PlateItem[];
  goals: string[];
}

export const MAX_PACK = 8;
export const packSlug = (category: string, age: string) => `${category}-${age.replace("+", "plus")}`;

export function packs(plates: PlateItem[], taxonomy: Taxonomy): Pack[] {
  const goalName = new Map(taxonomy.goals.map((g) => [g.slug, g.name]));
  const out: Pack[] = [];
  const ages = [...taxonomy.ages].sort((a, b) => a.level - b.level);
  for (const age of ages) {
    for (const category of taxonomy.categories) {
      const set = plates.filter((p) => p.category === category.slug && p.age === age.slug);
      const color = set.filter((p) => KIND_GROUP[p.kind] === "kleurplaat");
      const learn = set.filter((p) => KIND_GROUP[p.kind] === "leren");
      const make = set.filter((p) => KIND_GROUP[p.kind] === "knutselen" || KIND_GROUP[p.kind] === "tekenen");
      if (set.length < 5 || learn.length + make.length === 0 || color.length === 0) continue;
      const chosen = [...color.slice(0, 3), ...learn.slice(0, 3), ...make.slice(0, 2)];
      for (const p of set) { if (chosen.length >= MAX_PACK) break; if (!chosen.includes(p)) chosen.push(p); }
      const order = (p: PlateItem) => ({ kleurplaat: 0, leren: 1, tekenen: 2, knutselen: 3 })[KIND_GROUP[p.kind]];
      chosen.sort((a, b) => order(a) - order(b));
      const goals = [...new Set(chosen.flatMap((p) => p.goals))].map((g) => goalName.get(g)).filter((g): g is string => !!g);
      out.push({ slug: packSlug(category.slug, age.slug), category, age: { slug: age.slug, name: age.name }, plates: chosen, goals });
    }
  }
  return out;
}
