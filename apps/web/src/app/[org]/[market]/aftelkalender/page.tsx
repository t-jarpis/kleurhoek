import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { AdventCalendar } from "@/components/AdventCalendar";
import { Crumbs } from "@/components/Crumbs";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { adventDoors, doorOrder, openUntil } from "@/lib/advent";
import { api, NotFound } from "@/lib/api";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { absolute, hreflang, indexable, jsonLd, pageMeta, pageUrl } from "@/lib/seo";

export const revalidate = 300;
type Params = { params: Promise<{ org: string; market: string }> };

async function load(org: string, market: string) {
  const [plates, season] = await Promise.all([api.plates(market, org), api.season(market, org)]).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  const today = season.today.slice(0, 10);
  const year = openUntil(today).year;
  const { doors, target } = adventDoors(plates, year);
  return { doors, target, today, ...openUntil(today, target) };
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(market);
  const { target, doors } = await load(org, market);
  const title = t.advent.title[target];
  const o = await getOrg(org);
  return {
    title, description: t.advent.meta, ...pageMeta(o, market, "/aftelkalender"),
    ...(indexable(o) && doors[0] ? { openGraph: { title, description: t.advent.meta, type: "website", images: [absolute(market, doors[0].plate.svg.replace(/\.svg$/, ".png"))] } } : {}),
  };
}

/** Aftelkalender (ADR 0058): 24 deurtjes met een plaat, één per dag in december. */
export default async function AdventPage({ params }: Params) {
  const { org, market } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  const { doors, target, today, year, open, nightsTo, daysToStart } = await load(org, market);
  const day = today.slice(5, 7) === "12" ? Number(today.slice(8, 10)) : null;
  const title = t.advent.title[target];
  const status = nightsTo ? t.advent.nights[target](nightsTo) : daysToStart ? t.advent.startsIn(daysToStart) : open === 24 && day === null ? t.advent.archive : null;
  return (
    <div className="wrap" data-mode="kind">
      {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd({
        "@context": "https://schema.org", "@type": "CollectionPage", name: title, url: pageUrl(market, "/aftelkalender"), inLanguage: hreflang(market), description: t.advent.meta,
        mainEntity: { "@type": "ItemList", numberOfItems: doors.length, itemListElement: doors.filter((d) => d.day <= open).map((d) => ({ "@type": "ListItem", position: d.day, url: pageUrl(market, `/platen/${d.plate.slug}`), name: d.plate.name })) },
      }) }} />}
      <header className="mast"><div><Logo market={market} org={o} /></div></header>
      <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: title }]} />
      <div className="kh-advent-head">
        <h1 style={{ margin: 0 }}>{title}</h1>
        {status && <span className="kh-advent-count" role="status">{status}</span>}
      </div>
      <p className="lede">{t.advent.lede}</p>
      <AdventCalendar doors={doors} order={doorOrder(year)} open={open} today={day !== null && day <= 24 ? day : null} year={year} base={base} market={market} />
      <SiteFooter base={base} t={t} own={o.isDefault} />
      <Track event={{ type: "page_view", market, page: "aftelkalender" }} />
    </div>
  );
}
