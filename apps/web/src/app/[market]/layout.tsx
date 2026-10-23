import "@kleurhoek/theme/theme.css";
import "@kleurhoek/theme/ui.css";
import "../globals.css";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { LIVE_MARKETS, marketLanguage } from "@/lib/markets";

export const metadata: Metadata = {
  title: { default: "Kleurhoek", template: "%s · Kleurhoek" },
  description: "Zelf getekende kleurplaten om online in te kleuren of te printen.",
};

export default async function MarketLayout({ children, params }: { children: React.ReactNode; params: Promise<{ market: string }> }) {
  const { market } = await params;
  if (!LIVE_MARKETS.includes(market)) notFound();
  return (
    <html lang={marketLanguage(market)}>
      <body>{children}</body>
    </html>
  );
}

// Geen generateStaticParams: pagina's worden bij het eerste verzoek gebouwd en daarna gecachet (ISR),
// zodat een build niet afhangt van een draaiende API.
