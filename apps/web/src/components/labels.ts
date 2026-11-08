import type { PlateItem, Taxonomy } from "@/lib/types";

const FEEST = "var(--krijt-teal)";

/** Het label op een kaart: land of werelddeel in de wereldweergave, feestdag in de feestweergave, anders de categorie. */
/** Landnaam in de taal van de markt (ADR 0094); valt terug op de bronnaam. */
export const countryLabel = (country: string, t: Taxonomy) => t.countries?.find((c) => c.slug === country)?.name ?? country;

export function labelFor(p: PlateItem, t: Taxonomy, view: string): { text: string; color: string } {
  const cat = t.categories.find((c) => c.slug === p.category);
  if (p.world && (p.category === "wereld" || view === "wereld")) {
    const cont = t.continents.find((c) => c.slug === p.world!.continent);
    return { text: p.world.country ? countryLabel(p.world.country, t) : cont?.name ?? "", color: cont?.color ?? cat?.color ?? "var(--color-text-muted)" };
  }
  if (p.holiday && (p.category === "feest" || view === "feest")) {
    return { text: t.holidays.find((h) => h.slug === p.holiday)?.name ?? "", color: FEEST };
  }
  return { text: cat?.name ?? p.category, color: cat?.color ?? "var(--color-text-muted)" };
}
