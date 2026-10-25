import { Inject, Injectable } from "@nestjs/common";
import { eq } from "drizzle-orm";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { isVisible, seasonFor, type HolidayDef, type IsoDate, type PlateRule, type SeasonSpan, type SeasonView } from "./availability.domain";
import { holidayDates, holidays, plateRules, seasons } from "./availability.schema";

@Injectable()
export class AvailabilityService {
  constructor(@Inject(DB) private readonly db: Database) {}

  /** Filtert plaat-slugs op wat in dit land vandaag zichtbaar is. */
  async visibleSlugs(tenantId: string, slugs: string[], country: string, today: IsoDate): Promise<Set<string>> {
    const rules = await withTenant(this.db, tenantId, (tx) => tx.select().from(plateRules).where(eq(plateRules.tenantId, tenantId)));
    const bySlug = new Map<string, PlateRule>(rules.map((r) => [r.plateSlug, r]));
    return new Set(slugs.filter((s) => isVisible(bySlug.get(s), country, today)));
  }

  async season(tenantId: string, country: string, today: IsoDate): Promise<SeasonView> {
    const { hs, ds, ss } = await withTenant(this.db, tenantId, async (tx) => ({
      hs: await tx.select().from(holidays).where(eq(holidays.tenantId, tenantId)),
      ds: await tx.select().from(holidayDates).where(eq(holidayDates.tenantId, tenantId)),
      ss: await tx.select().from(seasons).where(eq(seasons.tenantId, tenantId)),
    }));
    const defs: HolidayDef[] = hs.map((h) => ({
      slug: h.slug, sortOrder: h.sortOrder, countries: h.countries,
      fixed: h.fixedMonth && h.fixedDay ? [h.fixedMonth, h.fixedDay] : null,
      dates: Object.fromEntries(ds.filter((d) => d.holidaySlug === h.slug).map((d) => [d.year, d.date])),
      leadDays: h.leadDays, afterDays: h.afterDays, approximate: h.approximate, label: h.label, overrides: h.overrides,
    }));
    const spans: SeasonSpan[] = ss.map((s) => ({ slug: s.slug, countries: s.countries, from: [s.fromMonth, s.fromDay], to: [s.toMonth, s.toDay], plateSlugs: s.plateSlugs }));
    return seasonFor(defs, spans, country, today);
  }

  /**
   * Feestdagen die in dit land gevierd worden, of null als we voor dit land geen kalender hebben (dan horen alle
   * feestdagen erbij, zoals op kleurhoek.com). ADR 0040.
   */
  async celebratedIn(tenantId: string, country: string): Promise<Set<string> | null> {
    const rows = await withTenant(this.db, tenantId, (tx) => tx.select({ slug: holidays.slug, countries: holidays.countries }).from(holidays).where(eq(holidays.tenantId, tenantId)));
    const c = country.toUpperCase();
    if (!rows.some((r) => r.countries.includes(c))) return null;
    return new Set(rows.filter((r) => r.countries.includes(c)).map((r) => r.slug));
  }

  /** Feestdagen die in dit land gevierd worden, in kalendervolgorde. */
  async holidaysFor(tenantId: string, country: string): Promise<string[]> {
    const rows = await withTenant(this.db, tenantId, (tx) => tx.select({ slug: holidays.slug, countries: holidays.countries, order: holidays.sortOrder }).from(holidays).where(eq(holidays.tenantId, tenantId)));
    const c = country.toUpperCase();
    const known = rows.some((r) => r.countries.includes(c));
    return rows.filter((r) => !known || r.countries.includes(c)).sort((a, b) => a.order - b.order).map((r) => r.slug);
  }
}
