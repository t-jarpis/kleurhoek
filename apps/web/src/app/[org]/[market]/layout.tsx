import "@kleurhoek/theme/theme.css";
import "@kleurhoek/theme/ui.css";
import "../../globals.css";
import { brandCss } from "@kleurhoek/theme";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { LIVE_MARKETS, marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { messages } from "@/i18n/nl";
import { hreflang, indexable, SITE } from "@/lib/seo";

type Params = Promise<{ org: string; market: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  const name = org && !org.isDefault ? org.name : "Kleurhoek";
  const seo = indexable(org) ? org!.seo : null;
  return {
    title: { default: name, template: `%s · ${name}` },
    description: messages(marketLanguage(market)).lede,
    // Alleen Kleurhoek zelf op het productiedomein in zoekmachines (ADR 0035).
    robots: indexable(org) ? { index: true, follow: true } : { index: false, follow: false },
    ...(indexable(org) ? { metadataBase: new URL(SITE), openGraph: { siteName: "Kleurhoek", type: "website", locale: hreflang(market).replace("-", "_") } } : {}),
    ...(seo?.googleVerification || seo?.bingVerification ? { verification: {
      ...(seo.googleVerification ? { google: seo.googleVerification } : {}),
      ...(seo.bingVerification ? { other: { "msvalidate.01": seo.bingVerification } } : {}),
    } } : {}),
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
