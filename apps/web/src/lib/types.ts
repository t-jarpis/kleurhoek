export interface PlateItem {
  slug: string; name: string; category: string; age: string;
  world: { continent: string; country: string | null } | null;
  holiday: string | null; svg: string;
}
export interface PlateDetail extends Omit<PlateItem, "svg"> {
  word: string | null; countQuestion: string | null; version: number; svg: string; regionCount: number;
  colorByNumber: {
    codes: string;
    palette: { number: number; code: string; hex: string; name: string }[];
    labels: { region: number; number: number; x: number; y: number; size: number }[];
  };
}
export interface Taxonomy {
  categories: { slug: string; color: string; name: string }[];
  ages: { slug: string; level: number; strokeWidth: number; name: string; hint: string | null }[];
  continents: { slug: string; color: string; name: string }[];
  holidays: { slug: string; name: string }[];
}
export interface Season {
  today: string;
  active: { kind: "season" | "holiday"; slug: string; name: string; date?: string; approximate?: boolean; label?: string | null }[];
  soon: { slug: string; name: string; date: string; approximate: boolean; label: string | null }[];
  plates: string[];
}
