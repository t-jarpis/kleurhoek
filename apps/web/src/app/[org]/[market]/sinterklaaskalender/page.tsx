import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { AdventCalendar } from "@/components/AdventCalendar";
import { Crumbs } from "@/components/Crumbs";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { doorOrder } from "@/lib/advent";
import { api, NotFound } from "@/lib/api";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { absolute, hreflang, indexable, jsonLd, pageMeta, pageUrl, pngOf } from "@/lib/seo";
import { dateLabel, hasSintCalendar, SINT_TEXT, sintDoors, sintOpen } from "@/lib/sint";

export const revalidate = 300;
type Params = { params: Promise<{ org: string; market: string }> };

async function load(org: string, market: string) {
  if (!hasSintCalendar(market)) notFound();
  const [plates, season] = await Promise.all([api.plates(market, org), api.season(market, org)]).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  const state = sintOpen(season.today.slice(0, 10), market);
  return { ...state, doors: sintDoors(plates, state.dates.length) };
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market } = await params;
  const { doors } = await load(org, market);
  const o = await getOrg(org);
  return {
    title: SINT_TEXT.title, description: SINT_TEXT.meta, ...pageMeta(o, market, "/sinterklaaskalender"),
    ...(indexable(o) && doors[0] ? { openGraph: { title: SINT_TEXT.title, description: SINT_TEXT.meta, type: "website", images: [absolute(market, pngOf(doors[0].plate.svg))] } } : {}),
  };
}

/** Sinterklaaskalender (ADR 0065): een deurtje per dag van de intocht tot pakjesavond, in nl-NL en nl-BE. */
export default async function SintCalendarPage({ params }: Params) {
  const { org, market } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  const { doors, dates, year, open, today, nightsTo, daysToStart } = await load(org, market);
  const status = today === dates.length ? SINT_TEXT.eve : nightsTo ? SINT_TEXT.nights(nightsTo) : daysToStart ? SINT_TEXT.startsIn(daysToStart, dateLabel(dates[0]!)) : open === dates.length && today === null ? SINT_TEXT.archive : null;
  return (
    <div className="wrap" data-mode="kind">
      {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd({
        "@context": "https://schema.org", "@type": "CollectionPage", name: SINT_TEXT.title, url: pageUrl(market, "/sinterklaaskalender"), inLanguage: hreflang(market), description: SINT_TEXT.meta,
        mainEntity: { "@type": "ItemList", numberOfItems: doors.length, itemListElement: doors.filter((d) => d.day <= open).map((d) => ({ "@type": "ListItem", position: d.day, url: pageUrl(market, `/platen/${d.plate.slug}`), name: d.plate.name })) },
      }) }} />}
      <header className="mast"><div><Logo market={market} org={o} /></div></header>
      <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: SINT_TEXT.title }]} />
      <div className="kh-advent-head">
        <h1 style={{ margin: 0 }}>{SINT_TEXT.title}</h1>
        {status && <span className="kh-advent-count" role="status">{status}</span>}
      </div>
      <p className="lede">{SINT_TEXT.lede}</p>
      <AdventCalendar kind="sint" total={dates.length} doors={doors} order={doorOrder(year, dates.length)} open={open} today={today} year={year} base={base} market={market}
        lockedLabels={dates.map((d, i) => SINT_TEXT.locked(i + 1, dateLabel(d)))} />
      <SiteFooter base={base} t={t} own={o.isDefault} />
      <Track event={{ type: "page_view", market, page: "sinterklaaskalender" }} />
    </div>
  );
}
