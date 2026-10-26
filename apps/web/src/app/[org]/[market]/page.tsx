import { AccountButton } from "@/components/AccountButton";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { BookButton, PickBar } from "@/components/BookPicker";
import { Fridge } from "@/components/Fridge";
import { Suspense } from "react";
import { notFound } from "next/navigation";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { messages } from "@/i18n/nl";
import { Browse } from "@/components/Browse";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { SeasonBand } from "@/components/SeasonBand";
import { Surprise } from "@/components/Surprise";
import { Track } from "@/components/Track";
import { SubscribeForm } from "@/components/SubscribeForm";
import { subscribe } from "./mail/actions";
import { getOrg } from "@/lib/org";
import { hreflang, indexable, jsonLd, pageMeta, SITE, pageUrl } from "@/lib/seo";
import type { Metadata } from "next";

export const revalidate = 300;

/** Titel en omschrijving van de voorpagina zijn per markt in te stellen in het admin panel (Vindbaarheid, ADR 0035). */
export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string }> }): Promise<Metadata> {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  const own = indexable(org) ? org!.seo?.home?.[hreflang(market)] : undefined;
  return {
    ...(own?.title ? { title: { absolute: own.title } } : {}),
    ...(own?.description ? { description: own.description } : {}),
    ...pageMeta(org, market, ""),
  };
}

export default async function Home({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org) notFound();
  const base = baseFor(org, market);
  const language = marketLanguage(market);
  const t = messages(market);
  const [plates, taxonomy, season] = await Promise.all([api.plates(market, slug), api.taxonomy(market, slug), api.season(market, slug)]).catch((e) => {
    if (e instanceof NotFound) notFound();
    throw e;
  });
  return (
    <div className="wrap" data-mode="kind">
      {indexable(org) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd({
        "@context": "https://schema.org", "@type": "WebSite", name: "Kleurhoek", url: pageUrl(market, ""), inLanguage: hreflang(market),
        description: org.seo?.home?.[hreflang(market)]?.description || t.lede, publisher: { "@type": "Organization", name: "Kleurhoek", url: SITE },
      }) }} />}
      <header className="mast">
        <div><Logo market={market} org={org} /><p className="lede">{t.lede}</p></div>
        <div className="row no-print"><BookButton language={language} /><Surprise market={market} slugs={plates.map((p) => p.slug)} label={t.surprise} />{org.features.accounts && <AccountButton market={market} t={{ login: t.login, account: t.account, logout: t.logout }} />}</div>
      </header>
      <SeasonBand season={season} plates={plates} taxonomy={taxonomy} market={market} base={base} t={t} />
      <Suspense fallback={null}><Browse plates={plates} taxonomy={taxonomy} market={market} language={language} /></Suspense>
      <Fridge market={market} plates={plates} language={language} />
      {org.isDefault && <SubscribeForm action={subscribe.bind(null, market)} language={language} />}
      <SiteFooter base={base} t={t} own={org.isDefault} />
      <PickBar market={market} language={language} />
      <Track event={{ type: "page_view", market, page: "home" }} />
    </div>
  );
}
