import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ColorToggle } from "@/components/ColorPreview";
import { Crumbs } from "@/components/Crumbs";
import { Logo } from "@/components/Logo";
import { PlateCard } from "@/components/PlateCard";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { api, NotFound } from "@/lib/api";
import { baseFor } from "@/lib/base";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";

export const revalidate = 600;
type Params = { params: Promise<{ org: string; market: string }> };

/** "Nieuw op de site" is er alleen in het Nederlands: de Public-notes (ADR 0030) zijn Nederlandse zinnen. */
const SITE_NEWS = "Nieuw op de site";
const day = (iso: string) => new Intl.DateTimeFormat("nl-NL", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).format(new Date(`${iso}T12:00:00Z`));

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(market);
  return { title: t.newTitle, description: t.newLede, ...pageMeta(await getOrg(org), market, "/nieuw") };
}

/** Wat is er nieuw (ADR 0080): de nieuwste platen, en in het Nederlands wat er op de site veranderde. */
export default async function NewPage({ params }: Params) {
  const { org, market } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  const dutch = marketLanguage(market) === "nl" && o.isDefault;
  const [plates, slugs, taxonomy, news] = await Promise.all([
    api.plates(market, org), api.newest(market), api.taxonomy(market, org), dutch ? api.news().catch(() => []) : Promise.resolve([]),
  ]).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  const bySlug = new Map(plates.map((p) => [p.slug, p]));
  const newest = slugs.map((s) => bySlug.get(s)).filter((p) => !!p);
  return (
    <div className="wrap" data-mode="kind">
      <header className="mast"><div><Logo market={market} org={o} /></div></header>
      <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: t.newTitle }]} />
      <main>
        <h1 className="page-title">{t.newTitle}</h1>
        <p className="lede">{t.newLede}</p>
        <div className="frow frow-end"><ColorToggle label={t.colorPreview} /></div>
        <div className="grid">
          {newest.map((p) => <PlateCard key={p.slug} plate={p} base={base} taxonomy={taxonomy} yr={t.yr} kindLabel={p.kind !== "kleurplaat" ? t.kindNames[p.kind] : undefined} />)}
        </div>
        {news.length > 0 && (
          <section className="kh-prose" aria-labelledby="site-news">
            <h2 id="site-news">{SITE_NEWS}</h2>
            {news.map((n) => (
              <div key={n.date}>
                <h3><time dateTime={n.date}>{day(n.date)}</time></h3>
                <ul>{n.notes.map((x) => <li key={x}>{x}</li>)}</ul>
              </div>
            ))}
          </section>
        )}
      </main>
      <SiteFooter base={base} t={t} market={market} own={o.isDefault} />
      <Track event={{ type: "page_view", market, page: "nieuw" }} />
    </div>
  );
}
