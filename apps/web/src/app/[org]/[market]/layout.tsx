import "@kleurhoek/theme/theme.css";
import "@kleurhoek/theme/ui.css";
import "../../globals.css";
import { brandCss } from "@kleurhoek/theme";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { LIVE_MARKETS, marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";

type Params = Promise<{ org: string; market: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const org = await getOrg((await params).org);
  const name = org && !org.isDefault ? org.name : "Kleurhoek";
  return {
    title: { default: name, template: `%s · ${name}` },
    description: "Zelf getekende kleurplaten om online in te kleuren of te printen.",
    ...(org && !org.isDefault ? { robots: { index: false } } : {}),
  };
}

/**
 * Het [org]-segment komt van de proxy: die zet de host om naar een organisatie (ADR 0017) en
 * herschrijft het pad. Zo bouwt en cachet Next.js elke pagina per organisatie apart.
 */
export default async function MarketLayout({ children, params }: { children: React.ReactNode; params: Params }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org || !LIVE_MARKETS.includes(market) || (org.offer.markets && !org.offer.markets.includes(market))) notFound();
  const css = brandCss(org.brand.colors);
  return (
    <html lang={marketLanguage(market)} {...(org.brand.theme ? { "data-kh-theme": org.brand.theme } : {})} {...(org.brand.font ? { "data-kh-font": org.brand.font } : {})}>
      {/* Nooit een lege string in <head>: browsers gooien tekst daar weg, dan klopt de hydratie niet en verdwijnt de CSS. */}
      <head>{css ? <style id="kh-brand">{css}</style> : null}</head>
      <body>{children}</body>
    </html>
  );
}

// Geen generateStaticParams: pagina's worden bij het eerste verzoek gebouwd en daarna gecachet (ISR),
// zodat een build niet afhangt van een draaiende API.
