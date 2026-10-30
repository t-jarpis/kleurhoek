import { createHash } from "node:crypto";
import { goalName, localizeSvg, SOURCE_LANGUAGE } from "@kleurhoek/catalog-data";
import { Inject, Injectable } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { todayIn } from "../../shared/dates";
import { AvailabilityService } from "../availability/availability.service";
import { CatalogService, GOALS, KIND_GROUPS, type PlateKind, type PlateSummary } from "../catalog/catalog.service";
import { LocalizationService, type Market } from "../localization/localization.service";
import { offerAllows } from "../organizations/offer";
import type { OrgFeatures, OrgOffer } from "../organizations/organizations.schema";
import { ShopService } from "../shop/shop.service";
import { SourcesService } from "../sources/sources.service";

/**
 * Wat een organisatie laat zien (ADR 0017, 0036). Zonder organisatie: alles, met winkel. `allowed` zijn de platen
 * uit de gekozen collecties (null = geen beperking).
 */
export interface View { offer: OrgOffer; features: OrgFeatures; allowed: ReadonlySet<string> | null }
export const FULL_VIEW: View = {
  offer: { markets: null, categories: null, ages: null, kinds: null, collections: null, goals: null, excluded: [] },
  features: { shop: true, accounts: true, learningFilters: false }, allowed: null,
};
const inView = (p: PlateSummary, view: View) => offerAllows(p, view.offer, view.allowed);

/** Knip-, vouw- en lijmlijnen van knutselplaten. Zelfde afspraken als in de CSS van de website. */
export const CRAFT_STYLE = ".cut{fill:none;stroke:#1d1b22;stroke-width:1;stroke-dasharray:4 3}.fold{fill:none;stroke:#1d1b22;stroke-width:.8;stroke-dasharray:1 2.5}.glue{fill:#d5d9de;stroke:#9aa1a9;stroke-width:.6}.tip{font:600 6px Nunito,system-ui,sans-serif;fill:#4a5260}";

export interface PlateFilter { kind?: string | undefined; category?: string | undefined; age?: string | undefined; continent?: string | undefined; country?: string | undefined; holiday?: string | undefined }

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
    private readonly shop: ShopService,
    private readonly sources: SourcesService,
  ) {}

  private get tenant() { return this.env.TENANT_ID; }

  market(code: string): Promise<Market | null> { return this.i18n.liveMarket(this.tenant, code); }

  /** De View van een organisatie: aanbod, functies en de platen uit haar collecties. */
  async viewOf(o: { offer: OrgOffer; features: OrgFeatures }): Promise<View> {
    return { offer: o.offer, features: o.features, allowed: await this.catalog.collectionPlates(this.tenant, o.offer.collections) };
  }

  /** Codes van alle markten die live staan (kleine letters, zoals in de URL). */
  liveMarkets(): Promise<string[]> { return this.i18n.liveMarkets(this.tenant); }

  /**
   * Adres van de SVG. In een andere taal dan de brontaal staat de taal erin plus een korte hash van de
   * vertaalde teksten: een verbeterde vertaling geeft een nieuw adres, dus het CDN mag elk adres voor altijd bewaren.
   */
  private svgPath(p: PlateSummary, language: string = SOURCE_LANGUAGE, texts: string[] = [], glossary?: Map<string, string>) {
    if (language === SOURCE_LANGUAGE || !glossary || !texts.length) return `/v1/assets/plates/${p.slug}/${p.version}.svg`;
    const rev = createHash("sha1").update(texts.map((t) => `${t}\u0000${glossary.get(t) ?? ""}`).join("\u0001")).digest("hex").slice(0, 8);
    return `/v1/assets/plates/${p.slug}/${p.version}.${language}-${rev}.svg`;
  }

  /** De woordenlijst en teksten per plaat, alleen nodig buiten de brontaal (ADR 0029). */
  private async textLayer(language: string, list: PlateSummary[]) {
    if (language === SOURCE_LANGUAGE) return null;
    const [glossary, texts] = await Promise.all([this.i18n.glossary(this.tenant, language), this.catalog.publishedTexts(this.tenant, list)]);
    return { glossary, texts };
  }

  /**
   * Gepubliceerde, vertaalde en zichtbare platen voor een markt, met de namen in de taal van de markt.
   * Vertaald betekent: een naam in die taal, en elke tekst in de plaat staat in de woordenlijst (ADR 0003, 0029).
   */
  private async visible(market: Market, now: Date, view: View = FULL_VIEW) {
    const all = (await this.catalog.listPublished(this.tenant)).filter((p) => inView(p, view));
    const names = await this.i18n.translate(this.tenant, "plate", market.language, all.map((p) => p.slug));
    const named = all.filter((p) => names.get(p.slug)?.name);
    const layer = await this.textLayer(market.language, named);
    const translated = layer ? named.filter((p) => (layer.texts.get(p.slug) ?? []).every((t) => layer.glossary.has(t))) : named;
    const shown = await this.availability.visibleSlugs(this.tenant, translated.map((p) => p.slug), market.country, todayIn(market.country, now));
    // Platen bij een feestdag die in dit land niet gevierd wordt (Koningsdag in België), niet tonen (ADR 0040).
    const celebrated = await this.availability.celebratedIn(this.tenant, market.country);
    if (celebrated) for (const p of translated) if (p.holiday && !celebrated.has(p.holiday)) shown.delete(p.slug);
    const path = (p: PlateSummary) => this.svgPath(p, market.language, layer?.texts.get(p.slug), layer?.glossary);
    return { plates: translated.filter((p) => shown.has(p.slug)), names, path };
  }

  async listPlates(market: Market, filter: PlateFilter, view: View = FULL_VIEW, now = new Date()) {
    const { plates, names, path } = await this.visible(market, now, view);
    const items = plates.filter((p) =>
      (!filter.kind || p.kind === filter.kind || KIND_GROUPS[p.kind as PlateKind] === filter.kind) &&
      (!filter.category || p.category === filter.category || (filter.category === "wereld" && p.continent) || (filter.category === "feest" && p.holiday)) &&
      (!filter.age || p.age === filter.age) &&
      (!filter.continent || p.continent === filter.continent) &&
      (!filter.country || p.depictedCountry === filter.country) &&
      (!filter.holiday || p.holiday === filter.holiday));
    return items.map((p) => ({
      slug: p.slug, name: names.get(p.slug)!.name, category: p.category, age: p.age,
      world: p.continent ? { continent: p.continent, country: p.depictedCountry } : null,
      holiday: p.holiday, svg: path(p), kind: p.kind, goals: p.goals,
    }));
  }

  async plate(market: Market, slug: string, view: View = FULL_VIEW, now = new Date()) {
    const detail = await this.catalog.getPublished(this.tenant, slug);
    if (!detail || !inView(detail, view)) return null;
    const [tr] = [(await this.i18n.translate(this.tenant, "plate", market.language, [slug])).get(slug)];
    if (!tr?.name) return null;
    const visible = await this.availability.visibleSlugs(this.tenant, [slug], market.country, todayIn(market.country, now));
    if (!visible.has(slug)) return null;
    const layer = await this.textLayer(market.language, [detail]);
    const texts = layer?.texts.get(slug) ?? [];
    if (layer && !texts.every((t) => layer.glossary.has(t))) return null;
    const local = (svg: string) => (layer ? localizeSvg(svg, (t) => layer.glossary.get(t)).svg : svg);
    const colorNames = await this.i18n.translate(this.tenant, "color", market.language, detail.colorByNumber.palette.map((c) => c.code));
    const needs = await this.catalog.materialsOf(this.tenant, slug);
    const [materialNames, offers] = await Promise.all([
      this.i18n.translate(this.tenant, "material", market.language, needs.map((m) => m.slug)),
      view.features.shop ? this.shop.forMaterials(market.code, market.language, needs.map((m) => m.slug)) : Promise.resolve(new Map()),
    ]);
    return {
      slug, name: tr.name, word: tr.word ?? null, countQuestion: tr.countQuestion ?? null,
      category: detail.category, age: detail.age, holiday: detail.holiday,
      world: detail.continent ? { continent: detail.continent, country: detail.depictedCountry } : null,
      version: detail.version, svg: this.svgPath(detail, market.language, texts, layer?.glossary), regionCount: detail.regionCount,
      colorByNumber: {
        codes: detail.colorByNumber.codes,
        palette: detail.colorByNumber.palette.map((c, i) => ({ number: i + 1, code: c.code, hex: c.hex, name: colorNames.get(c.code)?.name ?? c.code })),
        labels: detail.colorByNumber.labels,
      },
      kind: detail.kind, height: detail.height, minutes: detail.minutes, adultHelp: detail.adultHelp, paperGsm: detail.paperGsm,
      difficulty: detail.difficulty, goals: detail.goals,
      // Extra pagina's (ADR 0027): antwoordblad of extra vel, met titel uit de vertaling.
      pages: detail.pages.map((page, i) => ({ role: page.role, height: page.height, svg: local(page.svg), title: tr.pageTitles?.split("\n")[i] ?? `Pagina ${i + 2}`, number: i + 2 })),
      steps: tr.steps ? tr.steps.split("\n").filter(Boolean) : [],
      printNote: tr.printNote ?? null,
      // Wat je nodig hebt, met (als er een is) een product om door te klikken. Voor ouders, zie ADR 0011.
      materials: needs.filter((m) => materialNames.has(m.slug)).map((m) => ({
        slug: m.slug, optional: m.optional, name: materialNames.get(m.slug)!.name, hint: materialNames.get(m.slug)!.hint ?? null,
        product: offers.get(m.slug) ?? null,
      })),
    };
  }

  /** Doorverwijzing naar een product; alleen voor producten die in deze markt getoond worden. */
  async productLink(market: Market, product: string, plate: string | undefined, view: View = FULL_VIEW) {
    if (!view.features.shop) return null;
    return this.shop.link(market.code, product, plate ? `kleurhoek-${plate}` : "kleurhoek");
  }

  async taxonomy(market: Market, view: View = FULL_VIEW) {
    const t = await this.catalog.taxonomy(this.tenant);
    const [cat, age, cont, hol] = await Promise.all([
      this.i18n.translate(this.tenant, "category", market.language),
      this.i18n.translate(this.tenant, "age", market.language),
      this.i18n.translate(this.tenant, "continent", market.language),
      this.i18n.translate(this.tenant, "holiday", market.language),
    ]);
    const holidays = await this.availability.holidaysFor(this.tenant, market.country);
    return {
      categories: t.categories.filter((c) => cat.has(c.slug) && (!view.offer.categories || view.offer.categories.includes(c.slug))).map((c) => ({ ...c, name: cat.get(c.slug)!.name })),
      ages: t.ages.filter((a) => age.has(a.slug) && (!view.offer.ages || view.offer.ages.includes(a.slug))).map((a) => ({ ...a, name: age.get(a.slug)!.name, hint: age.get(a.slug)!.hint ?? null })),
      continents: t.continents.filter((c) => cont.has(c.slug)).map((c) => ({ ...c, name: cont.get(c.slug)!.name })),
      holidays: holidays.filter((h) => hol.has(h)).map((slug) => ({ slug, name: hol.get(slug)!.name })),
      // Leerdoelen (ADR 0036): namen staan in de website (vaste lijst); het filter staat aan per organisatie.
      goals: GOALS.filter((g) => !view.offer.goals || view.offer.goals.includes(g)).map((slug) => ({ slug, name: goalName(slug, market.language) })),
      learningFilters: view.features.learningFilters,
    };
  }

  async season(market: Market, orgView: View = FULL_VIEW, now = new Date()) {
    const today = todayIn(market.country, now);
    const view = await this.availability.season(this.tenant, market.country, today);
    const [hol, sea] = await Promise.all([
      this.i18n.translate(this.tenant, "holiday", market.language),
      this.i18n.translate(this.tenant, "season", market.language),
    ]);
    const { plates } = await this.visible(market, now, orgView);
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

  // ---------- Voor mails (ADR 0037) ----------

  /**
   * Platen voor een mail in een markt, met dezelfde regels als de site (vertaald, zichtbaar, in het aanbod).
   * `slugs` in die volgorde; anders op holiday of nieuw sinds `since`. Geeft naam en afbeeldingsadres (PNG).
   */
  async mailPlates(code: string, pick: { slugs?: string[] | undefined; holiday?: string | undefined; since?: Date | undefined }, max: number, now = new Date()) {
    const market = await this.market(code);
    if (!market) return [];
    const { plates, names, path } = await this.visible(market, now);
    let list = plates;
    if (pick.since) {
      const order = await this.catalog.publishedSince(this.tenant, pick.since);
      const bySlug = new Map(plates.map((p) => [p.slug, p]));
      list = order.map((s) => bySlug.get(s)).filter((p): p is PlateSummary => !!p);
    } else if (pick.slugs) {
      const bySlug = new Map(plates.map((p) => [p.slug, p]));
      list = pick.slugs.map((s) => bySlug.get(s)).filter((p): p is PlateSummary => !!p);
    } else if (pick.holiday) list = plates.filter((p) => p.holiday === pick.holiday);
    return list.slice(0, max).map((p) => ({ slug: p.slug, name: names.get(p.slug)!.name ?? p.slug, image: `${path(p).replace(/\.svg$/, ".png")}?r=2` }));
  }

  /** Feestdagen in een markt die binnen `days` dagen beginnen, met naam in de taal van de markt. */
  async upcomingHolidays(code: string, days: number, now = new Date()) {
    const market = await this.market(code);
    if (!market) return [];
    const today = todayIn(market.country, now);
    const view = await this.availability.season(this.tenant, market.country, today);
    const names = await this.i18n.translate(this.tenant, "holiday", market.language);
    const limit = Date.parse(`${today}T00:00:00Z`) + days * 86_400_000;
    const seen = new Set<string>();
    return [...view.active, ...view.soon]
      .filter((h) => h.date >= today && Date.parse(`${h.date}T00:00:00Z`) <= limit && !seen.has(h.slug) && seen.add(h.slug))
      .map((h) => ({ slug: h.slug, date: h.date, name: names.get(h.slug)?.name ?? h.slug }));
  }

  /**
   * Bronnengids (ADR 0025): thema's met links naar de makers. Alleen eigen tekst en links; nooit beeld
   * van de maker. Producten bij een thema alleen als de organisatie de winkel aan heeft.
   */
  async themes(market: Market) {
    const list = await this.sources.published(market.language);
    return list.map((t) => ({ slug: t.slug, name: t.name!, description: t.description, makerName: t.makerName, sourceCount: t.sources.length }));
  }

  async theme(market: Market, slug: string, view: View = FULL_VIEW) {
    const t = (await this.sources.published(market.language)).find((x) => x.slug === slug);
    if (!t) return null;
    const products = view.features.shop ? await this.shop.forProducts(market.code, market.language, t.productSlugs) : [];
    return {
      slug: t.slug, name: t.name!, description: t.description, makerName: t.makerName, makerUrl: t.makerUrl,
      sources: t.sources.map((s) => ({ title: s.title!, description: s.description, url: s.url, host: s.host, basis: s.basis })),
      products,
    };
  }

  /**
   * De SVG als losse afbeelding: met een eigen stijlblok, zodat hij ook in een <img> en via het CDN
   * goed getoond wordt. De lijndikte past bij de leeftijd en is te overschrijven met de CSS-variabele --sw.
   */
  async svg(slug: string, version: number, language: string = SOURCE_LANGUAGE) {
    const [raw, detail, taxonomy, glossary] = await Promise.all([
      this.catalog.getSvg(this.tenant, slug, version),
      this.catalog.getPublished(this.tenant, slug),
      this.catalog.taxonomy(this.tenant),
      language === SOURCE_LANGUAGE ? Promise.resolve(null) : this.i18n.glossary(this.tenant, language),
    ]);
    if (!raw || !detail) return null;
    // Teksten in de taal van de bezoeker (ADR 0029). Ontbrekende vertalingen blijven in de brontaal staan;
    // zo'n plaat is in die taal toch niet zichtbaar.
    const text = language === SOURCE_LANGUAGE ? raw : localizeSvg(raw, (t) => glossary!.get(t)).svg;
    const sw = taxonomy.ages.find((a) => a.slug === detail.age)?.strokeWidth ?? 2.4;
    const style = `<style>.r{fill:#fff;stroke:#1d1b22;stroke-width:var(--sw,${sw});stroke-linejoin:round}.l{fill:none;stroke:#1d1b22;stroke-width:var(--sw,${sw});stroke-linecap:round;stroke-linejoin:round}.dot{fill:#1d1b22}${CRAFT_STYLE}</style>`;
    return text.replace(/^(<svg[^>]*>)/, `$1${style}`);
  }
}
