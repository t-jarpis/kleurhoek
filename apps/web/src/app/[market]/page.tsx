import { Suspense } from "react";
import { notFound } from "next/navigation";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { messages } from "@/i18n/nl";
import { Browse } from "@/components/Browse";
import { Logo } from "@/components/Logo";
import { SeasonBand } from "@/components/SeasonBand";
import { Surprise } from "@/components/Surprise";
import { Track } from "@/components/Track";

export const revalidate = 300;

export default async function Home({ params }: { params: Promise<{ market: string }> }) {
  const { market } = await params;
  const language = marketLanguage(market);
  const t = messages(language);
  const [plates, taxonomy, season] = await Promise.all([api.plates(market), api.taxonomy(market), api.season(market)]).catch((e) => {
    if (e instanceof NotFound) notFound();
    throw e;
  });
  return (
    <div className="wrap">
      <header className="mast">
        <div><Logo market={market} /><p className="lede">{t.lede}</p></div>
        <div className="row no-print"><Surprise market={market} slugs={plates.map((p) => p.slug)} label={t.surprise} /></div>
      </header>
      <SeasonBand season={season} plates={plates} taxonomy={taxonomy} market={market} t={t} />
      <Suspense fallback={null}><Browse plates={plates} taxonomy={taxonomy} market={market} language={language} /></Suspense>
      <p className="note">{t.note}</p>
      <Track event={{ type: "page_view", market }} />
    </div>
  );
}
