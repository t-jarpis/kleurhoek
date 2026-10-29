import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Crumbs } from "@/components/Crumbs";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { api, NotFound } from "@/lib/api";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { packs } from "@/lib/packs";
import { pageMeta } from "@/lib/seo";
import { link } from "@/lib/sites";

export const revalidate = 300;
type Params = { params: Promise<{ org: string; market: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(market);
  return { title: t.packs.title, description: t.packs.meta, ...pageMeta(await getOrg(org), market, "/lespakketten") };
}

/** Overzicht van de lespakketten (ADR 0059), per leeftijd. */
export default async function PacksPage({ params }: Params) {
  const { org, market } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  const [plates, taxonomy] = await Promise.all([api.plates(market, org), api.taxonomy(market, org)]).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  const all = packs(plates, taxonomy);
  const ages = [...new Map(all.map((p) => [p.age.slug, p.age])).values()];
  return (
    <div className="wrap" data-mode="ouder">
      <header className="mast"><div><Logo market={market} org={o} /></div></header>
      <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: t.packs.title }]} />
      <h1 className="page-title">{t.packs.title}</h1>
      <p className="lede">{t.packs.lede}</p>
      {ages.map((age) => (
        <section key={age.slug} aria-labelledby={`age-${age.slug}`}>
          <h2 id={`age-${age.slug}`} className="sec">{t.packs.forAge(age.name)}</h2>
          <ul className="kh-packs">
            {all.filter((p) => p.age.slug === age.slug).map((p) => (
              <li key={p.slug}>
                <Link className="kh-pack" href={link(base, `/lespakketten/${p.slug}`)}>
                  <div className="kh-pack-thumbs">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    {p.plates.slice(0, 4).map((x) => <img key={x.slug} src={x.svg} alt="" loading="lazy" />)}
                  </div>
                  <h3>{t.packs.packTitle(p.category.name, p.age.name)}</h3>
                  <p>{t.packs.plates(p.plates.length)}</p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
      <SiteFooter base={base} t={t} own={o.isDefault} />
      <Track event={{ type: "page_view", market, page: "lespakket" }} />
    </div>
  );
}
