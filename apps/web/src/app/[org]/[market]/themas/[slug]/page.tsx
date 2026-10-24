import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { api, NotFound } from "@/lib/api";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";

export const revalidate = 300;

async function load(org: string, market: string, slug: string) {
  try { return await api.theme(market, slug, org); } catch (e) { if (e instanceof NotFound) notFound(); throw e; }
}

export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string; slug: string }> }): Promise<Metadata> {
  const { org, market, slug } = await params;
  const th = await load(org, market, slug);
  return { title: `Kleurplaten ${th.name}`, description: th.description ?? `Kleurplaten van ${th.name}, gratis bij ${th.makerName}.`, ...pageMeta(await getOrg(org), market, `/themas/${slug}`, false) };
}

const Arrow = () => <svg className="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8" /></svg>;

/**
 * Eén thema: links naar de maker (nieuw tabblad, zonder doorgeven van onze pagina) en eventueel echte
 * producten met partnerlink. Nooit beeld of tekst van de maker (ADR 0025).
 */
export default async function ThemePage({ params }: { params: Promise<{ org: string; market: string; slug: string }> }) {
  const { org: orgSlug, market, slug } = await params;
  const org = await getOrg(orgSlug);
  if (!org) notFound();
  const t = messages(marketLanguage(market));
  const th = await load(orgSlug, market, slug);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "thema" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={`/${market}/themas`}>{t.allThemes}</a></header>
      <h1 className="page-title">{th.name}</h1>
      {th.description && <p className="lede">{th.description}</p>}
      <ul className="kh-sources">
        {th.sources.map((s) => (
          <li key={s.url} className="kh-source">
            <div><b>{s.title}</b>{s.description && <span>{s.description}</span>}<span>{s.host}</span></div>
            <a className="ui-btn" href={s.url} target="_blank" rel="noopener noreferrer nofollow">{t.toMaker} <Arrow /></a>
          </li>
        ))}
      </ul>
      <p className="disclosure">{t.themeNotice(th.makerName)}</p>
      {th.products.length > 0 && (
        <section className="parents kh-theme-products">
          <h2>{t.themeProducts}</h2>
          <ul className="kh-sources">
            {th.products.map((p) => (
              <li key={p.slug} className="kh-source">
                <div><b>{p.name}</b>{p.note && <span>{p.note}</span>}</div>
                <a className="offer" href={`/ga/${p.slug}?plaat=thema-${th.slug}&m=${market}`} rel="sponsored nofollow noopener" target="_blank">
                  <span>{t.toShop}{p.priceHint ? ` · ${p.priceHint}` : ""}</span><small>{t.atPartner(p.partner)}</small>
                </a>
              </li>
            ))}
          </ul>
          <p className="disclosure">{t.partnerDisclosure}</p>
        </section>
      )}
      <SiteFooter market={market} t={t} own={org.isDefault} />
    </div>
  );
}
