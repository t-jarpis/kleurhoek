import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Booklet, type BookPlate } from "@/components/Booklet";
import { labelFor } from "@/components/labels";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { parseBook } from "@/lib/studio";
import { messages } from "@/i18n/nl";

export const metadata: Metadata = { title: "Kleurboekje", robots: { index: false } };

/**
 * Het boekje: voorblad plus de gekozen platen, elk op een eigen A4. De keuze staat in de URL
 * (`?platen=kat,vis`), zodat een boekje te delen is en er niets op de server bewaard hoeft te worden.
 */
export default async function BookPage({ params, searchParams }: { params: Promise<{ market: string }>; searchParams: Promise<{ platen?: string | string[] }> }) {
  const { market } = await params;
  const slugs = parseBook((await searchParams).platen);
  const language = marketLanguage(market);
  const t = messages(language);

  const taxonomy = await api.taxonomy(market).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  const load = async (slug: string): Promise<BookPlate | null> => {
    try {
      const plate = await api.plate(market, slug);
      const { inner } = await api.plateSvgInner(plate.svg);
      const age = taxonomy.ages.find((a) => a.slug === plate.age);
      const label = labelFor({ ...plate, svg: "" }, taxonomy, "alle").text;
      return { plate, inner, ageWidth: age?.strokeWidth ?? 2.4, foot: `Kleurhoek · ${label} · ${age?.name ?? plate.age}` };
    } catch (e) {
      if (e instanceof NotFound) return null; // niet (meer) beschikbaar in deze markt: stilletjes overslaan
      throw e;
    }
  };
  const [items, mascots] = await Promise.all([
    Promise.all(slugs.map(load)),
    Promise.all(["uil", "slak"].map((s) => load(s).then((m) => m?.inner ?? null))),
  ]);
  return <Booklet market={market} language={language} items={items.filter((i): i is BookPlate => i !== null)} mascots={mascots} title={t.book} />;
}
