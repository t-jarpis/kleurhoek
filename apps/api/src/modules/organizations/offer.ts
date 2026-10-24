import type { OrgOffer } from "./organizations.schema";

/** Wat een plaat moet hebben om te kunnen toetsen of hij in het aanbod valt. */
export interface OfferPlate { slug: string; category: string; age: string; kind: string; goals: readonly string[] }

/**
 * Valt een plaat binnen het aanbod van een organisatie (ADR 0017, 0036)? `allowed` zijn de platen uit de gekozen
 * collecties (null als de organisatie geen collecties kiest); die haalt de aanroeper bij Catalogus op.
 */
export function offerAllows(p: OfferPlate, offer: OrgOffer, allowed: ReadonlySet<string> | null): boolean {
  if (offer.categories && !offer.categories.includes(p.category)) return false;
  if (offer.ages && !offer.ages.includes(p.age)) return false;
  if (offer.kinds && !offer.kinds.includes(p.kind === "kleurplaat" ? "kleurplaat" : "knutselen")) return false;
  if (allowed && !allowed.has(p.slug)) return false;
  if (offer.goals && !p.goals.some((g) => offer.goals!.includes(g))) return false;
  if (offer.excluded.includes(p.slug)) return false;
  return true;
}

/** Wat een beheerder van de organisatie zelf mag aanpassen (ADR 0036). Markten, huisstijl en functies niet. */
export type SelfOffer = Pick<OrgOffer, "collections" | "goals" | "excluded">;
