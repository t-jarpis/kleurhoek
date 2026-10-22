import { Inject, Injectable } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { todayIn } from "../../shared/dates";
import { AvailabilityService } from "../availability/availability.service";
import { CatalogService, type PlateSummary } from "../catalog/catalog.service";
import { LocalizationService, type Market } from "../localization/localization.service";

export interface PlateFilter { category?: string | undefined; age?: string | undefined; continent?: string | undefined; country?: string | undefined; holiday?: string | undefined }

/**
 * Leesmodel voor de website. Combineert de publieke interfaces van Catalogus, Lokalisatie en
 * Beschikbaarheid; leest zelf geen tabellen. Regel: een plaat is zichtbaar als hij gepubliceerd is,
 * vertaald in de taal van de markt, en volgens Beschikbaarheid zichtbaar in het land.
 */
@Injectable()
export class StorefrontService {
  constructor(
    @Inject(ENV) private readonly env: Env,
    private readonly catalog: CatalogService,
    private readonly i18n: LocalizationService,
    private readonly availability: AvailabilityService,
  ) {}

  private get tenant() { return this.env.TENANT_ID; }

  market(code: string): Promise<Market | null> { return this.i18n.liveMarket(this.tenant, code); }

  private svgPath(p: PlateSummary) { return `/v1/assets/plates/${p.slug}/${p.version}.svg`; }

  /** Gepubliceerde, vertaalde en zichtbare platen voor een markt, met de namen in de taal van de markt. */
  private async visible(market: Market, now: Date) {
    const all = await this.catalog.listPublished(this.tenant);
    const names = await this.i18n.translate(this.tenant, "plate", market.language, all.map((p) => p.slug));
    const translated = all.filter((p) => names.get(p.slug)?.name);
    const shown = await this.availability.visibleSlugs(this.tenant, translated.map((p) => p.slug), market.country, todayIn(market.country, now));
    return { plates: translated.filter((p) => shown.has(p.slug)), names };
  }

  async listPlates(market: Market, filter: PlateFilter, now = new Date()) {
    const { plates, names } = await this.visible(market, now);
    const items = plates.filter((p) =>
      (!filter.category || p.category === filter.category || (filter.category === "wereld" && p.continent) || (filter.category === "feest" && p.holiday)) &&
      (!filter.age || p.age === filter.age) &&
      (!filter.continent || p.continent === filter.continent) &&
      (!filter.country || p.depictedCountry === filter.country) &&
      (!filter.holiday || p.holiday === filter.holiday));
    return items.map((p) => ({
      slug: p.slug, name: names.get(p.slug)!.name, category: p.category, age: p.age,
      world: p.continent ? { continent: p.continent, country: p.depictedCountry } : null,
      holiday: p.holiday, svg: this.svgPath(p),
    }));
  }

  async plate(market: Market, slug: string, now = new Date()) {
    const detail = await this.catalog.getPublished(this.tenant, slug);
    if (!detail) return null;
    const [tr] = [(await this.i18n.translate(this.tenant, "plate", market.language, [slug])).get(slug)];
    if (!tr?.name) return null;
    const visible = await this.availability.visibleSlugs(this.tenant, [slug], market.country, todayIn(market.country, now));
    if (!visible.has(slug)) return null;
    const colorNames = await this.i18n.translate(this.tenant, "color", market.language, detail.colorByNumber.palette.map((c) => c.code));
    return {
      slug, name: tr.name, word: tr.word ?? null, countQuestion: tr.countQuestion ?? null,
      category: detail.category, age: detail.age, holiday: detail.holiday,
      world: detail.continent ? { continent: detail.continent, country: detail.depictedCountry } : null,
      version: detail.version, svg: this.svgPath(detail), regionCount: detail.regionCount,
      colorByNumber: {
        codes: detail.colorByNumber.codes,
        palette: detail.colorByNumber.palette.map((c, i) => ({ number: i + 1, code: c.code, hex: c.hex, name: colorNames.get(c.code)?.name ?? c.code })),
        labels: detail.colorByNumber.labels,
      },
    };
  }

  async taxonomy(market: Market) {
    const t = await this.catalog.taxonomy(this.tenant);
    const [cat, age, cont, hol] = await Promise.all([
      this.i18n.translate(this.tenant, "category", market.language),
      this.i18n.translate(this.tenant, "age", market.language),
      this.i18n.translate(this.tenant, "continent", market.language),
      this.i18n.translate(this.tenant, "holiday", market.language),
    ]);
    const holidays = await this.availability.holidaysFor(this.tenant, market.country);
    return {
      categories: t.categories.filter((c) => cat.has(c.slug)).map((c) => ({ ...c, name: cat.get(c.slug)!.name })),
      ages: t.ages.filter((a) => age.has(a.slug)).map((a) => ({ ...a, name: age.get(a.slug)!.name, hint: age.get(a.slug)!.hint ?? null })),
      continents: t.continents.filter((c) => cont.has(c.slug)).map((c) => ({ ...c, name: cont.get(c.slug)!.name })),
      holidays: holidays.filter((h) => hol.has(h)).map((slug) => ({ slug, name: hol.get(slug)!.name })),
    };
  }

  async season(market: Market, now = new Date()) {
    const today = todayIn(market.country, now);
    const view = await this.availability.season(this.tenant, market.country, today);
    const [hol, sea] = await Promise.all([
      this.i18n.translate(this.tenant, "holiday", market.language),
      this.i18n.translate(this.tenant, "season", market.language),
    ]);
    const { plates } = await this.visible(market, now);
    const bySlug = new Map(plates.map((p) => [p.slug, p]));
    const slugs = new Set<string>([
      ...view.active.flatMap((h) => plates.filter((p) => p.holiday === h.slug).map((p) => p.slug)),
      ...view.spans.flatMap((s) => s.plateSlugs),
      ...view.soon.flatMap((h) => plates.filter((p) => p.holiday === h.slug).map((p) => p.slug)),
    ]);
    const name = (m: Map<string, Record<string, string | null>>, s: string) => m.get(s)?.name ?? s;
    return {
      today,
      active: [...view.spans.map((s) => ({ kind: "season" as const, slug: s.slug, name: name(sea, s.slug) })), ...view.active.map((h) => ({ kind: "holiday" as const, slug: h.slug, name: name(hol, h.slug), date: h.date, approximate: h.approximate, label: h.label }))],
      soon: view.soon.map((h) => ({ slug: h.slug, name: name(hol, h.slug), date: h.date, approximate: h.approximate, label: h.label })),
      plates: [...slugs].filter((s) => bySlug.has(s)).slice(0, 12),
    };
  }

  svg(slug: string, version: number) { return this.catalog.getSvg(this.tenant, slug, version); }
}
