import { AccountButton } from "@/components/AccountButton";
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
import { getOrg } from "@/lib/org";

export const revalidate = 300;

export default async function Home({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org) notFound();
  const language = marketLanguage(market);
  const t = messages(language);
  const [plates, taxonomy, season] = await Promise.all([api.plates(market, slug), api.taxonomy(market, slug), api.season(market, slug)]).catch((e) => {
    if (e instanceof NotFound) notFound();
    throw e;
  });
  return (
    <div className="wrap" data-mode="kind">
      <header className="mast">
        <div><Logo market={market} org={org} /><p className="lede">{t.lede}</p></div>
        <div className="row no-print"><BookButton language={language} /><Surprise market={market} slugs={plates.map((p) => p.slug)} label={t.surprise} />{org.features.accounts && <AccountButton market={market} t={{ login: t.login, account: t.account, logout: t.logout }} />}</div>
      </header>
      <SeasonBand season={season} plates={plates} taxonomy={taxonomy} market={market} t={t} />
      <Suspense fallback={null}><Browse plates={plates} taxonomy={taxonomy} market={market} language={language} /></Suspense>
      <Fridge market={market} plates={plates} language={language} />
      <SiteFooter market={market} t={t} own={org.isDefault} />
      <PickBar market={market} language={language} />
      <Track event={{ type: "page_view", market, page: "home" }} />
    </div>
  );
}
