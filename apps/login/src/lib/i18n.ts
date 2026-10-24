import { de } from "./locales/de";
import { en } from "./locales/en";
import { es } from "./locales/es";
import { fr } from "./locales/fr";
import { it } from "./locales/it";
import { pl } from "./locales/pl";
import { nl, type LoginMessages } from "./messages";

/** Talen van de inlogpagina; de eerste is de standaard. Meer talen: een bestand in locales/ en hier erbij. */
const ALL: Record<string, LoginMessages> = { nl, de, en, es, fr, it, pl };
export const LANGUAGES = () => Object.keys(ALL);

export const t = (language: string | undefined): LoginMessages => ALL[language ?? "nl"] ?? nl;

/**
 * Taal kiezen: eerst wat de site in het inlogverzoek meegeeft (ui_locales), anders de browser
 * (Accept-Language), anders Nederlands.
 */
export function pickLanguage(uiLocales: string[] | undefined, acceptLanguage: string | null): string {
  const wanted = [
    ...(uiLocales ?? []),
    ...(acceptLanguage ?? "").split(",").map((l) => l.split(";")[0]!.trim()),
  ].map((l) => l.slice(0, 2).toLowerCase()).filter(Boolean);
  return wanted.find((l) => l in ALL) ?? "nl";
}
