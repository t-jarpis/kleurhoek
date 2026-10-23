const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/;

/** Code uit de naam: kleine letters, zonder accenten, spaties en tekens worden streepjes. */
export function slugify(name: string): string {
  return name.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 32).replace(/-+$/g, "");
}

export function codeProblem(code: string, reserved: string[], taken: string[]): string | null {
  if (!code) return null;
  if (!SLUG.test(code)) return "Alleen kleine letters, cijfers en streepjes; niet beginnen of eindigen met een streepje.";
  if (code.endsWith("-dev")) return "Een code mag niet eindigen op -dev.";
  if (reserved.includes(code)) return "Deze code is gereserveerd.";
  if (taken.includes(code)) return "Er is al een organisatie met deze code.";
  return null;
}

