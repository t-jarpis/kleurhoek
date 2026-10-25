import type { Metadata } from "next";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { disclaimer } from "@/i18n/disclaimer";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";

export const revalidate = 3600;
export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string }> }): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(marketLanguage(market));
  return { title: t.disclaimer, description: t.metaDisclaimer, ...pageMeta(await getOrg(org), market, "/disclaimer") };
}

/** Disclaimer (ADR 0026), per taal een eigen tekst in i18n/disclaimer (ADR 0029). */
export default async function DisclaimerPage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org) notFound();
  const base = baseFor(org, market);
  const t = messages(marketLanguage(market));
  const Disclaimer = disclaimer(marketLanguage(market));
  const contact = (topic?: string) => link(base, `/contact${topic ? `?onderwerp=${topic}` : ""}`);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "disclaimer" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={link(base)}>{t.back}</a></header>
      <h1 className="page-title">{t.disclaimer}</h1>
      <article className="kh-prose">
        <Disclaimer base={base} contact={contact} />
      </article>
      <SiteFooter base={base} t={t} own={org.isDefault} />
    </div>
  );
}
