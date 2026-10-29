import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { messages } from "@/i18n/nl";
import { api, NotFound } from "@/lib/api";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { absolute, hreflang, indexable, jsonLd, pageMeta, pageUrl } from "@/lib/seo";
import { inTopic, topicTitle, topics, type Dimension } from "@/lib/topics";
import { Crumbs } from "./Crumbs";
import { Logo } from "./Logo";
import { PlateCard } from "./PlateCard";
import { SiteFooter } from "./SiteFooter";
import { TopicLinks } from "./TopicLinks";
import { Track } from "./Track";

type Params = { params: Promise<{ org: string; market: string; slug: string }> };

async function load(org: string, market: string, dim: Dimension, slug: string) {
  const [plates, taxonomy] = await Promise.all([api.plates(market, org), api.taxonomy(market, org)]).catch((e) => {
    if (e instanceof NotFound) notFound();
    throw e;
  });
  const t = messages(market);
  const groups = topics(plates, taxonomy, t);
  const topic = groups[dim].find((x) => x.slug === slug);
  if (!topic) notFound();
  return { plates: plates.filter((p) => inTopic(p, dim, slug)), taxonomy, groups, topic, t, title: topicTitle(t, topic) };
}

/**
 * Onderwerppagina (ADR 0055): alle platen van één onderwerp, feestdag, leeftijd, soort of werelddeel, op de server
 * gemaakt, met een eigen titel, korte tekst, kruimelpad en links naar de andere onderwerpen. Feestdagen bestaan
 * alleen in landen die ze vieren, dus taalversies (hreflang) alleen voor de andere dimensies.
 */
export function topicPage(dim: Dimension) {
  async function generateMetadata({ params }: Params): Promise<Metadata> {
    const { org, market, slug } = await params;
    const { plates, title, t } = await load(org, market, dim, slug);
    const description = t.topicMeta(title, plates.length);
    const o = await getOrg(org);
    const first = plates[0];
    return {
      title, description, ...pageMeta(o, market, `/${dim}/${slug}`, dim !== "feestdag"),
      ...(indexable(o) ? { openGraph: { title, description, type: "website", ...(first ? { images: [absolute(market, first.svg.replace(/\.svg$/, ".png"))] } : {}) } } : {}),
    };
  }

  async function Page({ params }: Params) {
    const { org, market, slug } = await params;
    const { plates, taxonomy, groups, t, title } = await load(org, market, dim, slug);
    const o = await getOrg(org);
    if (!o) notFound();
    const base = baseFor(o, market);
    const path = `/${dim}/${slug}`;
    return (
      <div className="wrap" data-mode="kind">
        {indexable(o) && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd([
          {
            "@context": "https://schema.org", "@type": "CollectionPage", name: title, url: pageUrl(market, path), inLanguage: hreflang(market),
            description: t.topicMeta(title, plates.length),
            mainEntity: { "@type": "ItemList", numberOfItems: plates.length, itemListElement: plates.slice(0, 100).map((p, i) => ({ "@type": "ListItem", position: i + 1, url: pageUrl(market, `/platen/${p.slug}`), name: p.name })) },
          },
          {
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            itemListElement: [{ name: "Kleurhoek", url: pageUrl(market, "") }, { name: title, url: pageUrl(market, path) }].map((c, i) => ({ "@type": "ListItem", position: i + 1, name: c.name, item: c.url })),
          },
        ]) }} />}
        <header className="mast">
          <div><Logo market={market} org={o} /></div>
        </header>
        <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: title }]} />
        <h1>{title}</h1>
        <p className="lede">{t.topicIntro(title, plates.length)}</p>
        <main className="grid">
          {plates.map((p) => (
            <PlateCard key={p.slug} plate={p} base={base} taxonomy={taxonomy} view={dim === "onderwerp" ? slug : "alle"} yr={t.yr}
              kindLabel={p.kind !== "kleurplaat" ? t.kindNames[p.kind] : undefined} alt={t.metaPlateTitle(p.name, t.kindNames[p.kind] ?? t.kindNames.kleurplaat!)} />
          ))}
        </main>
        <TopicLinks groups={groups} base={base} t={t} current={path} />
        <SiteFooter base={base} t={t} own={o.isDefault} />
        <Track event={{ type: "page_view", market, page: "onderwerp" }} />
      </div>
    );
  }

  return { generateMetadata, Page };
}
