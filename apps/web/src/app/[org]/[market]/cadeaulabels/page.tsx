import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Crumbs } from "@/components/Crumbs";
import { GiftLabels } from "@/components/GiftLabels";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { hreflang, indexable, jsonLd, pageMeta, pageUrl } from "@/lib/seo";
import { GIFT_TEXT, hasSintCalendar, SINT_TEXT } from "@/lib/sint";
import { link } from "@/lib/sites";

type Params = { params: Promise<{ org: string; market: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market } = await params;
  if (!hasSintCalendar(market)) notFound();
  const o = await getOrg(org);
  return { title: GIFT_TEXT.title, description: GIFT_TEXT.meta, ...pageMeta(o, market, "/cadeaulabels") };
}

/** Cadeaulabels en naamkaartjes met eigen naam (ADR 0067), in nl-NL en nl-BE. De naam blijft in de browser. */
export default async function GiftLabelsPage({ params }: Params) {
  const { org, market } = await params;
  if (!hasSintCalendar(market)) notFound();
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  return (
    <div className="wrap" data-mode="ouder">
      {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd({
        "@context": "https://schema.org", "@type": "WebPage", name: GIFT_TEXT.title, url: pageUrl(market, "/cadeaulabels"), inLanguage: hreflang(market), description: GIFT_TEXT.meta,
      }) }} />}
      <header className="mast no-print"><div><Logo market={market} org={o} /></div></header>
      <div className="no-print"><Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: SINT_TEXT.title, path: "/sinterklaaskalender" }, { name: GIFT_TEXT.nav }]} /></div>
      <main>
        <h1 className="no-print">{GIFT_TEXT.title}</h1>
        <p className="lede no-print">{GIFT_TEXT.lede}</p>
        <GiftLabels />
        <p className="no-print"><Link href={link(base, "/sinterklaaskalender")}>{SINT_TEXT.teaserCta}</Link></p>
      </main>
      <div className="no-print"><SiteFooter base={base} t={t} own={o.isDefault} /></div>
      <Track event={{ type: "page_view", market, page: "cadeaulabels" }} />
    </div>
  );
}
