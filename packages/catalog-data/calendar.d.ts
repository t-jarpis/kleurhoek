export const SINT_MARKETS: Record<string, number>;
export function intocht(year: number): string;
export function sintDates(year: number, market: string): string[];
export const SINT_FIRST: string[];
export const SINT_LAST: string;
export function sintDoorSlugs(slugs: string[], total: number): { day: number; slug: string }[];
export function sintDoorOn(date: string, market: string): { door: number; total: number } | null;
