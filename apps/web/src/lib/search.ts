/**
 * Zoeken in het platenraster (ADR 0084). Hoofdletters, accenten en leestekens maken niet uit; elk woord van de
 * zoekopdracht moet ergens voorkomen (naam, onderwerp, feestdag, werelddeel, land, soort). Een meervoud op -s,
 * -en of -es vindt ook het enkelvoud.
 */
export function fold(s: string): string {
  return s.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();
}

function stems(word: string): string[] {
  const out = [word];
  if (word.length > 4) for (const end of ["en", "es", "s", "e"]) if (word.endsWith(end)) {
    const stem = word.slice(0, -end.length);
    out.push(stem);
    // Verdubbelde medeklinker (dinosaurussen → dinosaurus, poppen → pop).
    if (/(.)\1$/.test(stem)) out.push(stem.slice(0, -1));
  }
  return out;
}

/** Maakt een zoekfunctie voor één zoekopdracht; null als er niets te zoeken is. */
export function matcher(query: string): ((haystack: string) => boolean) | null {
  const words = fold(query).split(" ").filter((w) => w.length > 0);
  if (!words.length) return null;
  return (haystack) => {
    const h = fold(haystack);
    return words.every((w) => stems(w).some((s) => h.includes(s)));
  };
}

/** Zoekwoord dat het bewaren waard is (de API controleert opnieuw): geen adres, nummer of e-mail. */
export function worthKeeping(query: string): boolean {
  const q = fold(query);
  return q.length >= 3 && q.length <= 40 && !/@|https?|www|\d{4,}/.test(query.toLowerCase()) && /\p{L}/u.test(q);
}
