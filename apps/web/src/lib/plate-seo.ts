import type { PlateExtra } from "@/i18n/plate-meta";
import type { PlateItem, Taxonomy } from "./types";

/** Onderwerp, leeftijd en andere namen van een plaat voor de meta-beschrijving (ADR 0085). */
export function plateExtra(plate: Pick<PlateItem, "category" | "age" | "also">, taxonomy: Taxonomy): PlateExtra {
  return {
    topic: taxonomy.categories.find((c) => c.slug === plate.category)?.name ?? null,
    age: taxonomy.ages.find((a) => a.slug === plate.age)?.name ?? null,
    also: plate.also ?? [],
  };
}
