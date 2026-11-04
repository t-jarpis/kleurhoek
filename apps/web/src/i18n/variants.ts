import { latamSpanish } from "./es-419";
import type { Messages } from "./nl-base";

/**
 * Teksten per markt (ADR 0047, 0050): een markt zonder eigen variant krijgt de teksten van zijn taal. Gedeeld door
 * de server (nl.ts, alle talen) en de browser (load.ts, alleen de eigen taal), zodat beide hetzelfde opleveren.
 */

/** Zelfde teksten met een andere schrijfwijze: elke tekst (ook wat een functie teruggeeft) gaat door `fix`. */
function variant<T>(value: T, fix: (s: string) => string): T {
  if (typeof value === "string") return fix(value) as T;
  if (typeof value === "function") return ((...a: unknown[]) => variant((value as (...a: unknown[]) => unknown)(...a), fix)) as T;
  if (Array.isArray(value)) return value.map((v) => variant(v, fix)) as T;
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, variant(v, fix)])) as T;
  return value;
}
/** Amerikaanse spelling en Letter-papier voor en-US (ADR 0047). */
export const usSpelling = (s: string) => s
  .replace(/([Cc])olour/g, "$1olor").replace(/([Ff])avourite/g, "$1avorite").replace(/([Oo])rganisation/g, "$1rganization")
  .replace(/on A4\b/g, "on letter paper").replace(/A4 sheet/g, "letter-size sheet").replace(/\bA4\b/g, "letter");
/** Zwitsers Duits schrijft geen ß (ADR 0047). */
export const swissSpelling = (s: string) => s.replace(/ß/g, "ss");
const letterPaper = (s: string) => s.replace(/on A4\b/g, "on letter paper").replace(/A4 sheet/g, "letter-size sheet").replace(/\bA4\b/g, "letter");

/** Markten met een eigen variant; de waarde maakt de variant uit de teksten van de taal. */
export const MARKET_VARIANTS: Record<string, (base: Messages) => Messages> = {
  "en-us": (en) => variant(en, usSpelling),
  "de-ch": (de) => variant(de, swissSpelling),
  "de-li": (de) => variant(de, swissSpelling),
  // Letter-papier in Canada (ADR 0050); Canadees Engels houdt de Britse spelling.
  "en-ca": (en) => variant(en, letterPaper),
  "fr-ca": (fr) => variant(fr, (s) => s.replace(/\bA4\b/g, "format lettre")),
  // Spaans voor Latijns-Amerika en de VS: ustedes in plaats van vosotros (ADR 0050).
  "es-mx": (es) => latamSpanish(es, true),
  "es-co": (es) => latamSpanish(es, true),
  "es-us": (es) => latamSpanish(es, true),
  "es-ar": (es) => latamSpanish(es, false),
};

/** Alle talen van de site (ADR 0054). */
export const LANGUAGES = ["nl", "de", "en", "es", "fr", "it", "pl", "pt", "sv", "da", "nb", "fi", "cs", "sk", "hu", "ro", "el", "bg", "hr", "sl", "et", "lv", "lt", "uk", "tr", "sr", "mk", "sq", "is"] as const;

/** Welke taal en welke variant bij een markt ("en-us") of taal ("en") horen; onbekend wordt Nederlands. */
export function resolve(marketOrLanguage: string): { language: string; variant: string | null } {
  const k = marketOrLanguage.toLowerCase();
  const language = (LANGUAGES as readonly string[]).includes(k.slice(0, 2)) ? k.slice(0, 2) : "nl";
  return { language, variant: MARKET_VARIANTS[k] && k.slice(0, 2) === language ? k : null };
}
