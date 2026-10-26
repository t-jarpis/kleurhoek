/** De oplossing van de rekenpuzzel uit het verborgen veld, als JSON (ADR 0048). Ongeldig = niet meesturen. */
export function powField(raw: string) {
  try {
    const p = JSON.parse(raw) as Record<string, unknown>;
    if (typeof p.challenge === "string" && typeof p.salt === "string" && typeof p.number === "number" && typeof p.expires === "number" && typeof p.signature === "string") {
      return { challenge: p.challenge, salt: p.salt, number: p.number, expires: p.expires, signature: p.signature };
    }
  } catch { /* geen oplossing */ }
  return undefined;
}
