import type { Metadata } from "next";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { OfferEditor } from "@/components/OfferEditor";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";

export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string }> }): Promise<Metadata> {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  return { title: messages(market).mgTitle(org?.name ?? ""), robots: { index: false, follow: false } };
}

/** Beheer door de organisatie zelf (ADR 0036): alleen op de site van een school, bso of bibliotheek. */
export default async function ManagePage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org || org.isDefault) notFound();
  const base = baseFor(org, market);
  const language = marketLanguage(market);
  const t = messages(market);
  return (
    <div className="wrap" data-mode="ouder">
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={link(base)}>{t.back}</a></header>
      <h1 className="page-title">{t.mgTitle(org.name)}</h1>
      <p className="lede">{t.mgIntro}</p>
      <OfferEditor org={org.slug} market={market} language={language} />
    </div>
  );
}
