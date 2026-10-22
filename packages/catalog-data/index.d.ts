export type Translations<T> = Record<string, T>;
export interface PlateSource {
  slug: string; order: number; category: string; age: string;
  world: { continent: string; country: string | null } | null;
  holiday: string | null; regionCount: number;
  colorByNumber: {
    codes: string;
    palette: { code: string; hex: string }[];
    labels: { region: number; number: number; x: number; y: number; size: number }[];
  };
  i18n: Translations<{ name: string; word: string | null; countQuestion: string | null }>;
}
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
export function plateSvg(slug: string): string;
