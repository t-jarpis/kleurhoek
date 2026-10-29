import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Crumbs } from "@/components/Crumbs";
import { Logo } from "@/components/Logo";
import { PlateCard } from "@/components/PlateCard";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { api, NotFound } from "@/lib/api";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { packs } from "@/lib/packs";
import { absolute, hreflang, indexable, jsonLd, pageMeta, pageUrl } from "@/lib/seo";
import { link } from "@/lib/sites";

export const revalidate = 300;
type Params = { params: Promise<{ org: string; market: string; slug: string }> };

async function load(org: string, market: string, slug: string) {
  const [plates, taxonomy] = await Promise.all([api.plates(market, org), api.taxonomy(market, org)]).catch((e) => { if (e instanceof NotFound) notFound(); throw e; });
  const pack = packs(plates, taxonomy).find((p) => p.slug === slug);
  if (!pack) notFound();
  return { pack, taxonomy };
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market, slug } = await params;
  const t = messages(market);
  const { pack } = await load(org, market, slug);
  const title = t.packs.packTitle(pack.category.name, pack.age.name);
  const description = t.packs.packMeta(pack.category.name, pack.age.name, pack.plates.length);
  const o = await getOrg(org);
  return {
    title, description, ...pageMeta(o, market, `/lespakketten/${slug}`),
    ...(indexable(o) ? { openGraph: { title, description, type: "website", images: [absolute(market, pack.plates[0]!.svg.replace(/\.svg$/, ".png"))] } } : {}),
  };
}

/** Eén lespakket (ADR 0059): uitleg voor de leerkracht, de platen in volgorde en alles in één keer printen. */
export default async function PackPage({ params }: Params) {
  const { org, market, slug } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  const { pack, taxonomy } = await load(org, market, slug);
  const title = t.packs.packTitle(pack.category.name, pack.age.name);
  const path = `/lespakketten/${slug}`;
  return (
    <div className="wrap" data-mode="ouder">
      {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd({
        "@context": "https://schema.org", "@type": "LearningResource", name: title, url: pageUrl(market, path), inLanguage: hreflang(market), isAccessibleForFree: true,
        description: t.packs.packMeta(pack.category.name, pack.age.name, pack.plates.length), educationalLevel: pack.age.name, learningResourceType: "Worksheet",
        ...(pack.goals.length ? { teaches: pack.goals } : {}),
        hasPart: pack.plates.map((p) => ({ "@type": "CreativeWork", name: p.name, url: pageUrl(market, `/platen/${p.slug}`) })),
      }) }} />}
      <header className="mast"><div><Logo market={market} org={o} /></div></header>
      <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: t.packs.title, path: "/lespakketten" }, { name: title }]} />
      <h1 className="page-title">{title}</h1>
      <p className="lede">{t.packs.intro(pack.plates.length)}</p>
      <div className="row no-print"><Link className="ui-btn" data-variant="primary" href={link(base, `/boekje?platen=${pack.plates.map((p) => p.slug).join(",")}`)}>{t.packs.printAll}</Link></div>
      <section className="kh-teacher">
        <h2>{t.packs.forTeacher}</h2>
        <p>{t.packs.teacherText}</p>
        {pack.goals.length > 0 && (<><h3>{t.packs.goals}</h3><ul>{pack.goals.map((g) => <li key={g}>{g}</li>)}</ul></>)}
      </section>
      <h2 className="sec">{t.packs.contents}</h2>
      <main className="grid">
        {pack.plates.map((p) => (
          <PlateCard key={p.slug} plate={p} base={base} taxonomy={taxonomy} view="alle" yr={t.yr}
            kindLabel={p.kind !== "kleurplaat" ? t.kindNames[p.kind] : undefined} alt={t.metaPlateTitle(p.name, t.kindNames[p.kind] ?? t.kindNames.kleurplaat!)} />
        ))}
      </main>
      <SiteFooter base={base} t={t} own={o.isDefault} />
      <Track event={{ type: "page_view", market, page: "lespakket" }} />
    </div>
  );
}
