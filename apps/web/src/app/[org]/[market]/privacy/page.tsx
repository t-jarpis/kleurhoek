import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { privacy } from "@/i18n/privacy";
import { baseFor } from "@/lib/base";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";
import { link } from "@/lib/sites";

export const revalidate = 3600;
export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string }> }): Promise<Metadata> {
  const { org, market } = await params;
  const { text } = privacy(marketLanguage(market));
  return { title: text.title, description: text.description, ...pageMeta(await getOrg(org), market, "/privacy") };
}

/** Privacybeleid (ADR 0069): een eigen pagina, ook voor de beoordeling van apps door Pinterest en Meta. */
export default async function PrivacyPage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org) notFound();
  const base = baseFor(org, market);
  const t = messages(market);
  const { text, lang } = privacy(marketLanguage(market));
  const contact = (topic?: string) => link(base, `/contact${topic ? `?onderwerp=${topic}` : ""}`);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "privacy" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={link(base)}>{t.back}</a></header>
      <main lang={lang}>
        <h1 className="page-title">{text.title}</h1>
        <article className="kh-prose"><text.Body contact={contact} /></article>
      </main>
      <SiteFooter base={base} t={t} own={org.isDefault} />
    </div>
  );
}
