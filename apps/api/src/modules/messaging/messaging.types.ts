/**
 * Berichten (ADR 0037): mails aan abonnees bij nieuwe platen, feestdagen en de nieuwsbrief. Typen die schema,
 * renderer, workflows en controllers delen.
 */

/** Waar je je voor kunt aanmelden. */
export const TOPICS = ["nieuwe-platen", "feestdagen", "nieuwsbrief"] as const;
export type Topic = (typeof TOPICS)[number];

/** Talen waarin mails kunnen; per tekst geldt: ontbreekt de taal, dan Nederlands. */
export type I18nText = Record<string, string>;

/** Blokken van een template (design system: MailBlockEditor). Alles wat een mail toont, staat hierin. */
export type Block =
  | { id: string; type: "heading"; text: I18nText }
  | { id: string; type: "text"; text: I18nText }
  | { id: string; type: "button"; label: I18nText; url: string }
  | { id: string; type: "plates"; source: PlateSource; collection?: string | undefined; slugs?: string[] | undefined; max: number; columns: 2 | 3 }
  | { id: string; type: "divider" };
export type BlockType = Block["type"];
/**
 * Welke platen een platenblok toont: `new` = gepubliceerd sinds de vorige keer (uit de aanleiding van de mail),
 * `holiday` = bij de feestdag die eraan komt, `collection` = een collectie, `selected` = met de hand gekozen.
 */
export const PLATE_SOURCES = ["new", "holiday", "collection", "selected"] as const;
export type PlateSource = (typeof PLATE_SOURCES)[number];

export const TEMPLATE_KINDS = ["system", "automation", "campaign"] as const;
export type TemplateKind = (typeof TEMPLATE_KINDS)[number];
/** Vaste templates die de code nodig heeft; ze zijn te bewerken, niet te verwijderen. */
export const SYSTEM_TEMPLATES = { confirm: "bevestigen", welcome: "welkom" } as const;

/** Aanleiding voor een workflow. */
export type Trigger =
  | { type: "subscribed" }
  | { type: "schedule"; weekday: number; hour: number }
  | { type: "plates_published"; min: number }
  | { type: "holiday_soon"; days: number };
export const TRIGGER_TYPES = ["subscribed", "schedule", "plates_published", "holiday_soon"] as const;

/** Stappen van een workflow, van boven naar beneden. */
export type Step =
  | { type: "filter"; topics?: Topic[] | undefined; markets?: string[] | undefined }
  | { type: "require_plates"; min: number }
  | { type: "wait"; hours: number }
  | { type: "send"; template: string };
export const STEP_TYPES = ["filter", "require_plates", "wait", "send"] as const;

/** Wat een mail meekrijgt van zijn aanleiding: sinds wanneer nieuw, welke feestdag. */
export interface MailContext { since?: string | undefined; holiday?: string | undefined; plates?: string[] | undefined; /** Alleen in de wachtrij tot de bevestigingsmail weg is. */ token?: string | undefined }

export interface Audience { topics: Topic[]; markets: string[] | null }
