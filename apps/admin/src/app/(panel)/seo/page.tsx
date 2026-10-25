import Link from "next/link";
import { BarList } from "@/components/charts/BarList";
import { num } from "@/components/charts/format";
import { StatCard } from "@/components/charts/StatCard";
import { TimeChart } from "@/components/charts/TimeChart";
import { adminApi, describe, type SearchEngine, type SearchMetric, type SearchReport } from "@/lib/api";
import { refreshSearch, saveSeo } from "./actions";
import { SnippetFields } from "./SnippetFields";

export const metadata = { title: "Vindbaarheid" };
export const dynamic = "force-dynamic";

/**
 * Vindbaarheid (ADR 0035, 0040, 0041). Tab Zoekcijfers: vertoningen, klikken en posities bij Google en Bing, naast
 * onze eigen tellingen van bezoekers via zoekmachines. Tab Instellingen: wat er in de sitemap komt, de voorpagina
 * per markt en de verificatiecodes. Alleen www.kleurhoek.nl, .be en .com worden geïndexeerd.
 */
const TABS = [["zoekcijfers", "Zoekcijfers"], ["instellingen", "Instellingen"]] as const;
type Tab = (typeof TABS)[number][0];
const PERIODS = [["7", "7 dagen"], ["28", "28 dagen"], ["90", "3 maanden"], ["365", "12 maanden"]] as const;
type Period = (typeof PERIODS)[number][0];
const ENGINE: Record<SearchEngine, string> = { google: "Google", bing: "Bing" };
const ENTRY_LABEL: Record<string, string> = { nl: "kleurhoek.nl", be: "kleurhoek.be", com: "kleurhoek.com" };
const iso = (d: Date) => d.toISOString().slice(0, 10);
const ctr = (m: SearchMetric) => (m.impressions ? `${(Math.round((m.clicks / m.impressions) * 1000) / 10).toString().replace(".", ",")}%` : "—");
const pos = (p: number | null) => (p === null ? "—" : (Math.round(p * 10) / 10).toString().replace(".", ","));
const when = (s: string) => new Intl.DateTimeFormat("nl-NL", { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Amsterdam" }).format(new Date(s));

function Zoekcijfers({ r, period, canManage }: { r: SearchReport; period: Period; canManage: boolean }) {
  const sum = (e: SearchEngine) => r.totals.find((t) => t.engine === e) ?? { clicks: 0, impressions: 0, position: null };
  const all = r.totals.reduce((m, t) => ({ clicks: m.clicks + t.clicks, impressions: m.impressions + t.impressions }), { clicks: 0, impressions: 0 });
  const ownTotal = r.own.reduce((n, o) => n + o.landings, 0);
  const days: string[] = [];
  for (let t = Date.parse(r.from); t <= Date.parse(r.to); t += 86_400_000) days.push(iso(new Date(t)));
  const at = (e: SearchEngine, k: "clicks" | "impressions") => { const m = new Map(r.series.filter((s) => s.engine === e).map((s) => [s.day, s[k]])); return days.map((d) => m.get(d) ?? 0); };
  const ready = r.configured.engines.length > 0 && r.configured.domains.length > 0;
  const table = (rows: (SearchMetric & { key: string })[], caption: string, label: string) => (
    <table>
      <caption className="visually-hidden">{caption}</caption>
      <thead><tr><th>{label}</th><th className="num">Klikken</th><th className="num">Vertoningen</th><th className="num">CTR</th><th className="num">Positie</th></tr></thead>
      <tbody>{rows.map((q) => <tr key={q.key}><td>{q.key}</td><td className="num">{num(q.clicks)}</td><td className="num">{num(q.impressions)}</td><td className="num">{ctr(q)}</td><td className="num">{pos(q.position)}</td></tr>)}</tbody>
    </table>
  );
  return (
    <>
      {!ready && (
        <section className="panel stack">
          <h2>Nog niet gekoppeld</h2>
          <div className="ui-callout"><p>De cijfers van Google en Bing komen binnen zodra de sleutels in de infrastructuur staan. Tot die tijd zie je hieronder alleen onze eigen telling van bezoekers die via een zoekmachine binnenkwamen.</p></div>
          <ol>
            <li><strong>Google:</strong> voeg in Search Console de domeinen kleurhoek.nl, kleurhoek.be en kleurhoek.com toe als <em>domeineigenschap</em> (verificatie via DNS). Maak in Google Cloud een serviceaccount, download de JSON-sleutel en voeg het e-mailadres van het serviceaccount in Search Console toe als gebruiker met beperkte rechten.</li>
            <li><strong>Bing:</strong> importeer de sites in Bing Webmaster Tools vanuit Search Console en maak onder Instellingen › API-toegang een API-sleutel.</li>
            <li>Zet het pad naar de JSON-sleutel en de Bing-sleutel in <code>infra/envs/prod/terraform.tfvars</code> (blok <code>search</code>) en draai <code>scripts/infra.sh up prod</code>.</li>
          </ol>
        </section>
      )}
      <div className="ui-stats dash-stats">
        <StatCard label="Klikken uit zoekmachines" value={all.clicks} period="" note={ready ? "Google en Bing samen" : "Nog niet gekoppeld"} />
        <StatCard label="Vertoningen in zoekresultaten" value={all.impressions} period="" note={`CTR ${ctr({ ...all, position: null })}`} />
        <StatCard label="Gemiddelde positie bij Google" value={Math.round((sum("google").position ?? 0) * 10) / 10} period="" note="Lager is beter" />
        <StatCard label="Bezoeken via zoekmachines" value={ownTotal} period="" note="Eigen telling: binnenkomsten met een zoekmachine als verwijzer" />
      </div>
      {r.series.length > 0 && (
        <section className="panel">
          <TimeChart title="Klikken per dag" bucket="day" dates={days} series={r.configured.engines.map((e, i) => ({ key: e, label: ENGINE[e], color: `var(--chart-${i + 1})`, values: at(e, "clicks") }))} />
        </section>
      )}
      {r.series.length > 0 && (
        <section className="panel">
          <TimeChart title="Vertoningen per dag" bucket="day" dates={days} series={r.configured.engines.map((e, i) => ({ key: e, label: ENGINE[e], color: `var(--chart-${i + 1})`, values: at(e, "impressions") }))} />
        </section>
      )}
      <div className="dash-grid">
        <section className="panel stack"><h2>Bezoeken per zoekmachine</h2><p className="lead">Eigen telling, zonder cookies.</p><BarList items={r.own.map((o) => ({ label: o.engine, value: o.landings }))} empty="Nog geen bezoeken via zoekmachines in deze periode." /></section>
        <section className="panel stack"><h2>Per domein</h2><p className="lead">Eigen telling: op welk domein kwamen ze binnen.</p><BarList items={r.ownByDomain.map((o) => ({ label: ENTRY_LABEL[o.entry] ?? o.entry, value: o.landings }))} empty="Nog geen bezoeken via zoekmachines in deze periode." /></section>
      </div>
      {r.sites.length > 0 && (
        <section className="panel stack">
          <h2>Per domein en zoekmachine</h2>
          <table>
            <caption className="visually-hidden">Zoekcijfers per domein</caption>
            <thead><tr><th>Domein</th><th>Zoekmachine</th><th className="num">Klikken</th><th className="num">Vertoningen</th><th className="num">CTR</th><th className="num">Positie</th></tr></thead>
            <tbody>{r.sites.map((s) => <tr key={`${s.site}-${s.engine}`}><td>{s.site}</td><td>{ENGINE[s.engine]}</td><td className="num">{num(s.clicks)}</td><td className="num">{num(s.impressions)}</td><td className="num">{ctr(s)}</td><td className="num">{pos(s.position)}</td></tr>)}</tbody>
          </table>
        </section>
      )}
      {r.queries.length > 0 && <section className="panel stack"><h2>Zoektermen</h2><p className="lead">Waarop mensen zochten toen ze Kleurhoek zagen (top 50, Google en Bing samen).</p>{table(r.queries, "Zoektermen", "Zoekterm")}</section>}
      {r.pages.length > 0 && <section className="panel stack"><h2>Pagina&apos;s</h2>{table(r.pages, "Pagina's in zoekresultaten", "Pagina")}</section>}
      {ready && (
        <section className="panel stack">
          <div className="row-between"><h2>Koppeling</h2>{canManage && <form action={refreshSearch}><button className="ui-btn" type="submit">Nu ophalen</button></form>}</div>
          <p className="lead">Elke 6 uur opgehaald. Google loopt 2 à 3 dagen achter, Bing geeft zoektermen per week. Periode {period} dagen.</p>
          <table>
            <caption className="visually-hidden">Laatste keer opgehaald</caption>
            <thead><tr><th>Domein</th><th>Zoekmachine</th><th>Laatst opgehaald</th><th>Cijfers tot</th><th>Stand</th></tr></thead>
            <tbody>{r.sync.map((s) => <tr key={`${s.site}-${s.engine}`}><td>{s.site}</td><td>{ENGINE[s.engine]}</td><td>{when(s.runAt)}</td><td>{s.lastDay ?? "—"}</td><td>{s.ok ? "In orde" : <span className="ui-badge" data-tone="danger">{s.message}</span>}</td></tr>)}</tbody>
          </table>
        </section>
      )}
    </>
  );
}

export default async function SeoPage({ searchParams }: { searchParams: Promise<{ melding?: string; tab?: string; periode?: string }> }) {
  const sp = await searchParams;
  const melding = sp.melding;
  const tab: Tab = TABS.some(([t]) => t === sp.tab) ? (sp.tab as Tab) : "zoekcijfers";
  const period: Period = PERIODS.some(([p]) => p === sp.periode) ? (sp.periode as Period) : "28";
  const href = (t: Tab, p: Period = period) => `/seo?tab=${t}&periode=${p}`;
  let data;
  try {
    const to = new Date(Date.now() - 86_400_000), from = new Date(to.getTime() - (Number(period) - 1) * 86_400_000);
    const [seo, me, report] = await Promise.all([adminApi.seo(), adminApi.me(), tab === "zoekcijfers" ? adminApi.searchReport(iso(from), iso(to)) : Promise.resolve(null)]);
    data = { seo, report, canManage: me.permissions.includes("seo.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { seo, report, canManage } = data;
  const site = `https://${seo.indexableHost}`;
  return (
    <>
      <div className="row-between dash-head">
        <div>
          <h1>Vindbaarheid</h1>
          <p className="lead">Hoe Kleurhoek in zoekmachines staat: hoe vaak we gevonden en aangeklikt worden, wat er in de sitemap komt, en de titel en omschrijving van de voorpagina per markt.</p>
        </div>
        {tab === "zoekcijfers" && <nav className="tabs" aria-label="Periode">
          {PERIODS.map(([p, label]) => <Link key={p} href={href(tab, p)} aria-current={p === period ? "page" : undefined}>{label}</Link>)}
        </nav>}
      </div>
      <div className="toolbar"><nav className="tabs" aria-label="Vindbaarheid">
        {TABS.map(([t, label]) => <Link key={t} href={href(t)} aria-current={t === tab ? "page" : undefined}>{label}</Link>)}
      </nav></div>
      {melding && <p className="note" role="status">{melding}</p>}
      {tab === "zoekcijfers" && report && <Zoekcijfers r={report} period={period} canManage={canManage} />}
      {tab === "instellingen" && <>
      <section className="panel">
        <h2>Wie wordt er gevonden</h2>
        <div className="ui-callout">
          <p><strong>Alleen {seo.indexableHosts.join(", ")}.</strong> Nederland op kleurhoek.nl, België op kleurhoek.be (Nederlands en Frans), andere landen op kleurhoek.com. De dev-omgeving, lokaal draaien en de sites van organisaties (scholen, bibliotheken, eigen domeinen) krijgen <code>noindex</code> en een robots.txt die alles afschermt. Zo komen er geen dubbele pagina&apos;s in zoekmachines en blijven sites van organisaties van hen.</p>
        </div>
        <p>Per domein een eigen robots.txt en sitemap, bijvoorbeeld <a href={`${site}/robots.txt`}>robots.txt</a> en <a href={`${site}/sitemap.xml`}>sitemap.xml</a> op {seo.indexableHost}. Elke plaat heeft een eigen titel, omschrijving in de taal van de markt, een vaste (canonieke) URL, taalversies en gestructureerde gegevens.</p>
        <table>
          <caption className="visually-hidden">In de sitemap per markt</caption>
          <thead><tr><th>Markt</th><th>Taal</th><th className="num">Platen</th><th className="num">Thema&apos;s</th><th className="num">Adressen in de sitemap</th></tr></thead>
          <tbody>{seo.markets.map((m) => <tr key={m.market}><td>{m.market}</td><td>{m.language}</td><td className="num">{m.plates}</td><td className="num">{m.themes}</td><td className="num">{5 + m.plates + m.themes}</td></tr>)}</tbody>
        </table>
      </section>
      <form action={saveSeo} className="stack">
        <fieldset disabled={!canManage} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
          <section className="panel stack">
            <h2>Aanmelden bij zoekmachines</h2>
            <p className="lead">Plak alleen de code uit de meta-tag (wat tussen <code>content=&quot;…&quot;</code> staat). Hij komt alleen op {seo.indexableHost}.</p>
            <label className="field"><span>Google Search Console</span><input name="googleVerification" defaultValue={seo.settings.googleVerification ?? ""} maxLength={100} pattern="[A-Za-z0-9_\-]{10,100}" autoComplete="off" spellCheck={false} className="mono" /><small>Eigenschap toevoegen › HTML-tag.</small></label>
            <label className="field"><span>Bing Webmaster Tools</span><input name="bingVerification" defaultValue={seo.settings.bingVerification ?? ""} maxLength={100} pattern="[A-Za-z0-9_\-]{10,100}" autoComplete="off" spellCheck={false} className="mono" /><small>Site toevoegen › HTML-metatag (msvalidate.01).</small></label>
          </section>
          {seo.markets.map((m) => (
            <section key={m.market} className="panel stack">
              <h2>Voorpagina {m.market}</h2>
              <SnippetFields market={m.market} host={seo.indexableHost} title={seo.settings.home[m.market]?.title ?? null} description={seo.settings.home[m.market]?.description ?? null} />
            </section>
          ))}
          {canManage && <div><button className="ui-btn" data-variant="primary" type="submit">Opslaan</button></div>}
        </fieldset>
      </form>
      </>}
    </>
  );
}
