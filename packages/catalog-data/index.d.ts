export type Translations<T> = Record<string, T>;
/** Soort werkje. Kleurplaten zijn de basis; de rest is knutselwerk. */
export type PlateKind = "kleurplaat" | "knipplaat" | "bouwplaat" | "spel" | "vouwblad" | "werkblad" | "sjabloon" | "kaart" | "tekenles";
export const KINDS: PlateKind[];
export type KindGroup = "kleurplaten" | "knutselen" | "leren" | "tekenen";
export const KIND_GROUPS: Record<PlateKind, KindGroup>;
/** Extra pagina bij een plaat (pagina 2, 3 …): een antwoordblad of een extra vel (onderdelen, stappen). */
export interface PageSource { role: "antwoorden" | "extra"; height: number }
export interface PlateMaterial { slug: string; optional: boolean }
export interface PlateSource {
  slug: string; order: number; category: string; age: string;
  world: { continent: string; country: string | null } | null;
  holiday: string | null; regionCount: number;
  kind: PlateKind;
  /** Hoogte van de tekening (viewBox 0 0 200 hoogte). Kleurplaten 200, knutselplaten vaak hoger (A4). */
  height: number;
  minutes: number | null;
  /** Een volwassene moet helpen (schaar, mesje). */
  adultHelp: boolean;
  paperGsm: number | null;
  /** 1 makkelijk, 2 gemiddeld, 3 uitdagend; null = niet aangegeven. */
  difficulty: 1 | 2 | 3 | null;
  /** Extra pagina's (bestanden plates/<slug>.p2.svg, .p3.svg …); titels in i18n.pageTitles. */
  pages: PageSource[];
  materials: PlateMaterial[];
  colorByNumber: {
    codes: string;
    palette: { code: string; hex: string }[];
    labels: { region: number; number: number; x: number; y: number; size: number }[];
  };
  /** De plaat is taalgebonden (woordpuzzel, letters, rijmen): alleen in de brontaal, niet vertalen (ADR 0029). */
  languageBound?: boolean;
  i18n: Translations<{ name: string; word: string | null; countQuestion: string | null; steps?: string[]; printNote?: string; pageTitles?: string[] }>;
}
export interface MaterialSource extends Named {}
export interface Named { slug: string; order: number; i18n: Translations<{ name: string; hint?: string }> }
export interface CategorySource extends Named { color: string }
export interface AgeSource extends Named { level: number; strokeWidth: number }
export interface ContinentSource extends Named { color: string }
export interface HolidaySource extends Named {
  fixed: [number, number] | null; dates: Record<string, string> | null;
  leadDays: number; afterDays: number; approximate: boolean; label: string | null; countries: string[];
}
export interface SeasonSource { slug: string; from: [number, number]; to: [number, number]; plates: string[]; countries: string[]; i18n: Translations<{ name: string }> }
export interface ColorSource { code: string; hex: string; i18n: Translations<{ name: string }> }
export function plates(): PlateSource[];
export function categories(): CategorySource[];
export function ages(): AgeSource[];
export function continents(): ContinentSource[];
export function holidays(): HolidaySource[];
export function seasons(): SeasonSource[];
export function colors(): ColorSource[];
export function materials(): MaterialSource[];
export function plateSvg(slug: string): string;
export function pageSvg(slug: string, n: number): string;
export function textLanguages(): string[];
export function texts(language: string): Record<string, string>;
/** Brontaal van de teksten in de SVG's. */
export const SOURCE_LANGUAGE: "nl";
export function isNeutral(text: string): boolean;
export function plateTexts(...svgs: string[]): string[];
export function localizeSvg(svg: string, lookup: (source: string) => string | undefined): { svg: string; missing: string[]; scaled: { source: string; text: string; from: number; to: number }[] };
export function width(text: string): number;
