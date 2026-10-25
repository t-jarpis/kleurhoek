// Pure domeinlogica voor beschikbaarheid en de feestdagenkalender. Geen database, dus goed te testen.

/** Een datum zonder tijd, als 'YYYY-MM-DD'. Rekenen gebeurt in UTC om tijdzonefouten te voorkomen. */
export type IsoDate = string;
const DAY = 86_400_000;
const toMs = (d: IsoDate) => Date.parse(`${d}T00:00:00Z`);
const toIso = (ms: number): IsoDate => new Date(ms).toISOString().slice(0, 10);

export interface PlateRule {
  plateSlug: string;
  mode: "everywhere_except" | "only_in";
  countries: string[];
  validFrom: IsoDate | null;
  validTo: IsoDate | null;
}

/** Is een plaat zichtbaar in dit land op deze dag? Geen regel = overal zichtbaar. */
export function isVisible(rule: PlateRule | undefined, country: string, today: IsoDate): boolean {
  if (!rule) return true;
  if (rule.validFrom && today < rule.validFrom) return false;
  if (rule.validTo && today > rule.validTo) return false;
  const listed = rule.countries.includes(country.toUpperCase());
  return rule.mode === "only_in" ? listed : !listed;
}

export interface HolidayDef {
  slug: string;
  sortOrder: number;
  countries: string[];
  fixed: [month: number, day: number] | null;
  /** Datums per jaar voor feestdagen zonder vaste datum. */
  dates: Record<number, IsoDate>;
  leadDays: number;
  afterDays: number;
  approximate: boolean;
  label: string | null;
  /** Per land een andere datum of omschrijving; `dates` per jaar. */
  overrides?: Record<string, HolidayOverride>;
}

export interface HolidayOverride { fixed?: [number, number] | null; dates?: Record<string, IsoDate>; label?: string | null }

/** De feestdag zoals hij in dit land valt: met de afwijkingen van dat land (Sinterklaas in België op 6 december). */
export function inCountry(h: HolidayDef, country: string): HolidayDef {
  const o = h.overrides?.[country.toUpperCase()];
  if (!o) return h;
  return {
    ...h,
    ...(o.fixed !== undefined || o.dates ? { fixed: o.dates ? null : o.fixed ?? null, dates: o.dates ? Object.fromEntries(Object.entries(o.dates).map(([y, d]) => [Number(y), d])) : h.dates } : {}),
    ...(o.label !== undefined ? { label: o.label } : {}),
  };
}

/** De eerstvolgende datum van een feestdag die nog niet voorbij is (inclusief de dagen erna). */
export function nextOccurrence(h: HolidayDef, today: IsoDate): IsoDate | null {
  const year = Number(today.slice(0, 4));
  for (const y of [year, year + 1]) {
    const date = h.fixed ? `${y}-${String(h.fixed[0]).padStart(2, "0")}-${String(h.fixed[1]).padStart(2, "0")}` : h.dates[y];
    if (date && toMs(date) + h.afterDays * DAY >= toMs(today)) return date;
  }
  return null;
}

export interface SeasonSpan { slug: string; countries: string[]; from: [number, number]; to: [number, number]; plateSlugs: string[] }

export interface SeasonView {
  /** Feestdagen die nu "aan" staan: binnen de voorlooptijd of de dagen erna. */
  active: { slug: string; date: IsoDate; approximate: boolean; label: string | null }[];
  /** Feestdagen die binnen de horizon beginnen. */
  soon: { slug: string; date: IsoDate; approximate: boolean; label: string | null }[];
  spans: { slug: string; plateSlugs: string[] }[];
}

export function seasonFor(holidays: HolidayDef[], spans: SeasonSpan[], country: string, today: IsoDate, horizonDays = 60): SeasonView {
  const c = country.toUpperCase();
  const now = toMs(today);
  const view: SeasonView = { active: [], soon: [], spans: [] };
  // Zonder kalender voor dit land (markten op kleurhoek.com): alle feestdagen (ADR 0040).
  const known = holidays.some((x) => x.countries.includes(c));
  for (const h of holidays.filter((x) => !known || x.countries.includes(c)).map((x) => inCountry(x, c))) {
    const date = nextOccurrence(h, today);
    if (!date) continue;
    const item = { slug: h.slug, date, approximate: h.approximate, label: h.label };
    if (toMs(date) - h.leadDays * DAY <= now) view.active.push(item);
    else if (toMs(date) - now <= horizonDays * DAY) view.soon.push(item);
  }
  view.active.sort((a, b) => a.date.localeCompare(b.date));
  view.soon.sort((a, b) => a.date.localeCompare(b.date));
  const md = today.slice(5);
  const knownSpans = spans.some((x) => x.countries.includes(c));
  for (const s of spans.filter((x) => !knownSpans || x.countries.includes(c))) {
    const from = `${String(s.from[0]).padStart(2, "0")}-${String(s.from[1]).padStart(2, "0")}`;
    const to = `${String(s.to[0]).padStart(2, "0")}-${String(s.to[1]).padStart(2, "0")}`;
    const inSpan = from <= to ? md >= from && md <= to : md >= from || md <= to;
    if (inSpan) view.spans.push({ slug: s.slug, plateSlugs: s.plateSlugs });
  }
  return view;
}

export { toIso as isoFromMs };
