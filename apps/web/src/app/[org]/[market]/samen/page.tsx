import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Crumbs } from "@/components/Crumbs";
import { JoinTogether } from "@/components/JoinTogether";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";
import { link } from "@/lib/sites";

type Params = { params: Promise<{ org: string; market: string }>; searchParams: Promise<{ fout?: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(market);
  return { title: t.together.title, description: t.together.meta, ...pageMeta(await getOrg(org), market, "/samen") };
}

/** Samen kleuren (ADR 0060): uitleg en een code invullen om mee te doen. */
export default async function TogetherPage({ params, searchParams }: Params) {
  const { org, market } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const t = messages(market);
  const base = baseFor(o, market);
  const gone = (await searchParams).fout === "code";
  return (
    <div className="wrap" data-mode="ouder">
      <header className="mast"><div><Logo market={market} org={o} /></div></header>
      <Crumbs base={base} label={t.crumbs} items={[{ name: "Kleurhoek", path: "" }, { name: t.together.title }]} />
      <h1 className="page-title">{t.together.title}</h1>
      <p className="lede">{t.together.lede}</p>
      {gone && <div className="ui-callout" role="alert"><p>{t.together.notFound}</p></div>}
      <JoinTogether market={market} href={link(base, "/samen")} />
      <h2 className="sec">{t.together.howTitle}</h2>
      <ol className="kh-steps-how">{t.together.how.map((s) => <li key={s}>{s}</li>)}</ol>
      <p className="hint">{t.together.expires}</p>
      <SiteFooter base={base} t={t} own={o.isDefault} />
      <Track event={{ type: "page_view", market, page: "samen" }} />
    </div>
  );
}
