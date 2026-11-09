import type { Metadata } from "next";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { notFound } from "next/navigation";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { ForParents } from "@/components/ForParents";
import { SiteFooter } from "@/components/SiteFooter";
import { Studio } from "@/components/Studio";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { kindFor } from "@/i18n/plate-meta";
import { plateExtra } from "@/lib/plate-seo";
import { getOrg } from "@/lib/org";
import { SITE, absolute, hreflang, indexable, jsonLd, pageMeta, pageUrl, pinOf, pngOf } from "@/lib/seo";
import Link from "next/link";
import { Crumbs } from "@/components/Crumbs";
import { PlateCard } from "@/components/PlateCard";
import { PinButton } from "@/components/PinButton";
import { topicTitle } from "@/lib/topics";

export const revalidate = 300;
/** Leeg: de pagina wordt bij het eerste verzoek gemaakt en daarna bewaard (ISR, ADR 0093). */
export function generateStaticParams() { return []; }

async function load(org: string, market: string, slug: string) {
  try {
    const [plate, taxonomy, all] = await Promise.all([api.plate(market, slug, org), api.taxonomy(market, org), api.plates(market, org)]);
    const { inner } = await api.plateSvgInner(plate.svg);
    // Vergelijkbare platen (ADR 0055): zelfde onderwerp, eerst dezelfde leeftijd, hooguit 12.
    const same = all.filter((p) => p.category === plate.category && p.slug !== plate.slug);
    const related = [...same.filter((p) => p.age === plate.age), ...same.filter((p) => p.age !== plate.age)].slice(0, 12);
    // Nog eentje erbij? (ADR 0076): eerst dezelfde soort en leeftijd, dan dezelfde leeftijd, dan de rest.
    const rank = (p: (typeof same)[number]) => (p.kind === plate.kind ? 0 : 2) + (p.age === plate.age ? 0 : 1);
    const more = [...same].sort((a, b) => rank(a) - rank(b)).slice(0, 3);
    return { plate, taxonomy, inner, related, more, categoryCount: same.length + 1 };
  } catch (e) {
    if (e instanceof NotFound) notFound();
    throw e;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string; slug: string }> }): Promise<Metadata> {
  const { org, market, slug } = await params;
  const { plate, taxonomy } = await load(org, market, slug);
  const t = messages(market);
  const kind = kindFor(plate.name, t.kindNames[plate.kind] ?? t.kindNames.kleurplaat!);
  // Zoekgerichte titel en beschrijving (ADR 0085): soort niet dubbel, met onderwerp, leeftijd en andere namen.
  const description = t.metaPlate(plate.name, kind, plateExtra(plate, taxonomy));
  const title = t.plateTitle(plate.name, kind);
  const o = await getOrg(org);
  const image = absolute(market, pngOf(plate.svg));
  return { title, description, ...pageMeta(o, market, `/platen/${slug}`, false), ...(indexable(o) ? { openGraph: { title, description, type: "article", images: [image] }, twitter: { card: "summary_large_image", images: [image] } } : {}) };
}

export default async function PlatePage({ params }: { params: Promise<{ org: string; market: string; slug: string }> }) {
  const { org, market, slug } = await params;
  const { plate, taxonomy, inner, related, more, categoryCount } = await load(org, market, slug);
  const ageWidth = taxonomy.ages.find((a) => a.slug === plate.age)?.strokeWidth ?? 2.4;
  const language = marketLanguage(market);
  const o = await getOrg(org);
  const base = baseFor(o, market);
  const t = messages(market);
  const kind = kindFor(plate.name, t.kindNames[plate.kind] ?? t.kindNames.kleurplaat!);
  const category = taxonomy.categories.find((c) => c.slug === plate.category);
  const topicPath = `/onderwerp/${plate.category}`;
  const topicName = category ? topicTitle(t, { dim: "onderwerp", slug: plate.category, name: category.name }) : null;
  return (
    <>
      {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd([
        {
          "@context": "https://schema.org", "@type": "CreativeWork", name: plate.name, url: pageUrl(market, `/platen/${plate.slug}`),
          description: t.metaPlate(plate.name, kind, plateExtra(plate, taxonomy)), inLanguage: hreflang(market), isAccessibleForFree: true,
          genre: kind, publisher: { "@type": "Organization", name: "Kleurhoek", url: SITE },
          image: { "@type": "ImageObject", contentUrl: absolute(market, pngOf(plate.svg)), thumbnailUrl: absolute(market, plate.svg), caption: t.metaPlateTitle(plate.name, kind) },
          ...(category ? { about: category.name } : {}),
          ...(plate.also?.length ? { alternateName: plate.also } : {}),
        },
        {
          "@context": "https://schema.org", "@type": "BreadcrumbList",
          itemListElement: [{ name: "Kleurhoek", url: pageUrl(market, "") }, ...(topicName ? [{ name: topicName, url: pageUrl(market, topicPath) }] : []), { name: plate.name, url: pageUrl(market, `/platen/${plate.slug}`) }]
            .map((c, i) => ({ "@type": "ListItem", position: i + 1, name: c.name, item: c.url })),
        },
      ]) }} />}
      <Track event={{ type: "page_view", market, page: "plaat", plate: plate.slug }} />
      <main><Studio plate={plate} inner={inner} ageWidth={ageWidth} market={market} language={language} accounts={o?.features.accounts ?? false} more={more} /></main>
      <div className="wrap after-studio" data-mode="ouder">
        <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, ...(topicName ? [{ name: topicName, path: topicPath }] : []), { name: plate.name }]} />
        {plate.also && plate.also.length > 0 && <p className="hint kh-also">{t.alsoKnownAs}: {plate.also.join(", ")}</p>}
        {indexable(o) && (
          <div className="kh-share no-print">
            <PinButton market={market} plate={plate.slug} label={t.pinSave} url={pageUrl(market, `/platen/${plate.slug}`)} title={t.metaPlateTitle(plate.name, kind)}
              href={`https://www.pinterest.com/pin/create/button/?${new URLSearchParams({ url: pageUrl(market, `/platen/${plate.slug}`), media: absolute(market, pinOf(market, plate.slug)), description: t.metaPlateTitle(plate.name, kind) })}`} />
            <span className="hint">{t.pinHint}</span>
          </div>
        )}
        <ForParents plate={plate} market={market} t={t} />
        {related.length > 0 && category && (
          <section className="no-print">
            <div className="ui-sectionhead"><h2>{t.moreIn(category.name)}</h2><Link href={link(base, topicPath)}>{t.seeAll(categoryCount)}</Link></div>
            <div className="grid">
              {related.map((p) => <PlateCard key={p.slug} plate={p} base={base} taxonomy={taxonomy} view={plate.category} yr={t.yr}
                kindLabel={p.kind !== "kleurplaat" ? t.kindNames[p.kind] : undefined} alt={t.metaPlateTitle(p.name, kindFor(p.name, t.kindNames[p.kind] ?? t.kindNames.kleurplaat!))} />)}
            </div>
          </section>
        )}
        <SiteFooter base={base} t={t} market={market} own={o?.isDefault ?? false} />
      </div>
    </>
  );
}
