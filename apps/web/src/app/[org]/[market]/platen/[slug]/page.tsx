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
import { getOrg } from "@/lib/org";
import { hreflang, indexable, jsonLd, pageMeta, SITE, pageUrl } from "@/lib/seo";

export const revalidate = 300;

async function load(org: string, market: string, slug: string) {
  try {
    const [plate, taxonomy] = await Promise.all([api.plate(market, slug, org), api.taxonomy(market, org)]);
    const { inner } = await api.plateSvgInner(plate.svg);
    return { plate, taxonomy, inner };
  } catch (e) {
    if (e instanceof NotFound) notFound();
    throw e;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string; slug: string }> }): Promise<Metadata> {
  const { org, market, slug } = await params;
  const { plate } = await load(org, market, slug);
  const t = messages(marketLanguage(market));
  const description = t.metaPlate(plate.name, t.kindNames[plate.kind] ?? t.kindNames.kleurplaat!);
  const o = await getOrg(org);
  return { title: plate.name, description, ...pageMeta(o, market, `/platen/${slug}`, false), ...(indexable(o) ? { openGraph: { title: plate.name, description, type: "article" } } : {}) };
}

export default async function PlatePage({ params }: { params: Promise<{ org: string; market: string; slug: string }> }) {
  const { org, market, slug } = await params;
  const { plate, taxonomy, inner } = await load(org, market, slug);
  const ageWidth = taxonomy.ages.find((a) => a.slug === plate.age)?.strokeWidth ?? 2.4;
  const language = marketLanguage(market);
  const o = await getOrg(org);
  const base = baseFor(o, market);
  const t = messages(language);
  return (
    <>
      {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd({
        "@context": "https://schema.org", "@type": "CreativeWork", name: plate.name, url: pageUrl(market, `/platen/${plate.slug}`),
        description: t.metaPlate(plate.name, t.kindNames[plate.kind] ?? t.kindNames.kleurplaat!), inLanguage: hreflang(market), isAccessibleForFree: true,
        genre: t.kindNames[plate.kind], publisher: { "@type": "Organization", name: "Kleurhoek", url: SITE },
      }) }} />}
      <Track event={{ type: "page_view", market, page: "plaat", plate: plate.slug }} />
      <Studio plate={plate} inner={inner} ageWidth={ageWidth} market={market} language={language} accounts={o?.features.accounts ?? false} />
      <div className="wrap after-studio" data-mode="ouder"><ForParents plate={plate} market={market} t={messages(language)} /><SiteFooter base={base} t={messages(language)} own={o?.isDefault ?? false} /></div>
    </>
  );
}
