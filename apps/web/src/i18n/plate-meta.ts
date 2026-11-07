/** Extra's in de meta-beschrijving van een plaat (ADR 0085): onderwerp, leeftijd en andere namen. */
export interface PlateExtra { topic?: string | null; age?: string | null; also?: string[] }

const fold = (s: string) => s.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();

/** De soort als hij nog niet in de naam staat ("Kaart: welkom thuis!" is al een kaart), anders leeg. */
export function kindFor(name: string, kind: string): string {
  return kind && fold(name).includes(fold(kind)) ? "" : kind;
}

/** Zin over de plaat, aangevuld met onderwerp en leeftijd ("Lekker eten · 4–6 jaar.") en andere namen. */
export function plateDescription(lead: string, extra: PlateExtra | undefined, alsoLabel: string): string {
  const parts = [lead];
  const facts = [extra?.topic, extra?.age].filter((x): x is string => !!x);
  if (facts.length) parts.push(`${facts.join(" · ")}.`);
  if (extra?.also?.length) parts.push(`${alsoLabel}: ${extra.also.join(", ")}.`);
  return parts.join(" ");
}
