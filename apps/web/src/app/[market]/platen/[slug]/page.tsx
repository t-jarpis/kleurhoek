import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { Studio } from "@/components/Studio";

export const revalidate = 300;

async function load(market: string, slug: string) {
  try {
    const [plate, taxonomy] = await Promise.all([api.plate(market, slug), api.taxonomy(market)]);
    const { inner } = await api.plateSvgInner(plate.svg);
    return { plate, taxonomy, inner };
  } catch (e) {
    if (e instanceof NotFound) notFound();
    throw e;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ market: string; slug: string }> }): Promise<Metadata> {
  const { market, slug } = await params;
  const { plate } = await load(market, slug);
  return { title: plate.name, description: `Kleurplaat ${plate.name}: online inkleuren of printen.` };
}

export default async function PlatePage({ params }: { params: Promise<{ market: string; slug: string }> }) {
  const { market, slug } = await params;
  const { plate, taxonomy, inner } = await load(market, slug);
  const ageWidth = taxonomy.ages.find((a) => a.slug === plate.age)?.strokeWidth ?? 2.4;
  return <Studio plate={plate} inner={inner} ageWidth={ageWidth} market={market} language={marketLanguage(market)} />;
}
