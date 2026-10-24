import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { ForParents } from "@/components/ForParents";
import { SiteFooter } from "@/components/SiteFooter";
import { Studio } from "@/components/Studio";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";

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
  return { title: plate.name, description: `Kleurplaat ${plate.name}: online inkleuren of printen.` };
}

export default async function PlatePage({ params }: { params: Promise<{ org: string; market: string; slug: string }> }) {
  const { org, market, slug } = await params;
  const { plate, taxonomy, inner } = await load(org, market, slug);
  const ageWidth = taxonomy.ages.find((a) => a.slug === plate.age)?.strokeWidth ?? 2.4;
  const language = marketLanguage(market);
  return (
    <>
      <Track event={{ type: "page_view", market, page: "plaat", plate: plate.slug }} />
      <Studio plate={plate} inner={inner} ageWidth={ageWidth} market={market} language={language} />
      <div className="wrap after-studio" data-mode="ouder"><ForParents plate={plate} market={market} t={messages(language)} /><SiteFooter market={market} t={messages(language)} /></div>
    </>
  );
}
