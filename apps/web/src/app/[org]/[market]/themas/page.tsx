import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";

export const revalidate = 300;
export const metadata: Metadata = { title: "Thema's bij de maker", description: "Kleurplaten van bekende figuren en plekken, gratis bij de makers zelf. Door Kleurhoek nagekeken." };

/** Bronnengids (ADR 0024): eigen tekst en een eigen letterteken per thema, geen beeld van de maker. */
export default async function ThemesPage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org) notFound();
  const t = messages(marketLanguage(market));
  const themes = await api.themes(market, slug).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  return (
    <div className="wrap" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "themas" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={`/${market}`}>{t.back}</a></header>
      <h1 className="page-title">{t.themesTitle}</h1>
      <p className="lede">{t.themesLede}</p>
      {themes.length === 0 ? (
        <div className="ui-empty"><p>{t.themesEmpty}</p></div>
      ) : (
        <div className="kh-themes">
          {themes.map((th) => (
            <Link key={th.slug} className="kh-theme-card" href={`/${market}/themas/${th.slug}`}>
              <span className="kh-theme-mark" aria-hidden="true">{th.name.slice(0, 1).toUpperCase()}</span>
              <span>
                <h3>{th.name}</h3>
                {th.description && <p>{th.description}</p>}
                <small>{t.byMaker(th.makerName)} · {t.themeSources(th.sourceCount)}</small>
              </span>
            </Link>
          ))}
        </div>
      )}
      <SiteFooter market={market} t={t} />
    </div>
  );
}
