import Link from "next/link";
import { BarList } from "@/components/charts/BarList";
import { num } from "@/components/charts/format";
import { StatCard } from "@/components/charts/StatCard";
import { TimeChart } from "@/components/charts/TimeChart";
import { WorldMap } from "@/components/charts/WorldMap";
import { adminApi, describe } from "@/lib/api";
import { REF_KIND_LABEL, refKind, type RefKind } from "@/lib/referrers";

export const dynamic = "force-dynamic";
export const metadata = { title: "Analytics" };

/**
 * Analytics (ADR 0034): eigen telling zonder cookies, IP-adres of profielen, in de geest van Matomo. Tabs voor
 * bezoekers, bronnen, inhoud, techniek en locatie, organisaties en "nu op de site". Het dashboard houdt de kern.
 */
const TABS = [["bezoekers", "Bezoekers"], ["bronnen", "Bronnen"], ["inhoud", "Inhoud"], ["techniek", "Apparaten en landen"], ["organisaties", "Organisaties"], ["nu", "Nu op de site"]] as const;
type Tab = (typeof TABS)[number][0];
const PERIODS = [["7", "7 dagen"], ["30", "30 dagen"], ["90", "90 dagen"], ["365", "12 maanden"]] as const;
type Period = (typeof PERIODS)[number][0];
const PERIOD_TEXT: Record<Period, string> = { "7": "vorige 7 dagen", "30": "vorige 30 dagen", "90": "vorige 90 dagen", "365": "vorige 12 maanden" };
const PAGE_LABEL: Record<string, string> = { home: "Home", plaat: "Plaatpagina's", boekje: "Boekje", account: "Account", "niet-gevonden": "Niet gevonden", disclaimer: "Disclaimer", contact: "Contact", themas: "Thema's", thema: "Themapagina's", "eigen-omgeving": "Eigen omgeving" };
const DEVICE_LABEL: Record<string, string> = { mobile: "Telefoon", tablet: "Tablet", desktop: "Computer", other: "Overig" };
const ENTRY_LABEL: Record<string, string> = { nl: "kleurhoek.nl", be: "kleurhoek.be", com: "kleurhoek.com" };
const iso = (d: Date) => d.toISOString().slice(0, 10);
const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 1000) / 10}%`.replace(".", ",") : "—");
const countryName = (code: string) => { try { return code ? new Intl.DisplayNames(["nl"], { type: "region" }).of(code) ?? code : "Onbekend"; } catch { return code || "Onbekend"; } };

export default async function Analytics({ searchParams }: { searchParams: Promise<{ tab?: string; periode?: string }> }) {
  const sp = await searchParams;
  const tab: Tab = TABS.some(([t]) => t === sp.tab) ? (sp.tab as Tab) : "bezoekers";
  const period: Period = PERIODS.some(([p]) => p === sp.periode) ? (sp.periode as Period) : "30";
  const to = new Date(), from = new Date(Date.now() - (Number(period) - 1) * 86_400_000);
  const href = (t: Tab, p: Period = period) => `/analytics?tab=${t}&periode=${p}`;
  let o, live, orgNames = new Map<string, string>();
  try {
    [o, live] = await Promise.all([adminApi.overview(iso(from), iso(to)), tab === "nu" ? adminApi.realtime() : Promise.resolve(null)]);
    if (tab === "organisaties") orgNames = new Map((await adminApi.organizations().catch(() => ({ organizations: [] as { slug: string; name: string }[] }))).organizations.map((x) => [x.slug, x.name]));
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const vs = PERIOD_TEXT[period];
  const dates = o.series.map((p) => p.date);
  const landings = o.entries.reduce((s, e) => s + e.landings, 0);
  const kinds = o.referrers.reduce((m, r) => m.set(refKind(r.referrer), (m.get(refKind(r.referrer)) ?? 0) + r.landings), new Map<RefKind, number>());

  return (
    <>
      <div className="row-between dash-head">
        <div><h1>Analytics</h1><p className="lead">{o.from} t/m {o.to}. Eigen telling zonder cookies, IP-adressen of profielen; bezoekers zijn per dag uniek. Bijgewerkt elke 10 minuten.</p></div>
        {tab !== "nu" && <nav className="tabs" aria-label="Periode">
          {PERIODS.map(([p, label]) => <Link key={p} href={href(tab, p)} aria-current={p === period ? "page" : undefined}>{label}</Link>)}
        </nav>}
      </div>
      <div className="toolbar"><nav className="tabs" aria-label="Analytics">
        {TABS.map(([t, label]) => <Link key={t} href={href(t)} aria-current={t === tab ? "page" : undefined}>{label}</Link>)}
      </nav></div>

      {tab === "bezoekers" && <>
        <div className="ui-stats dash-stats">
          <StatCard label="Bezoekers" value={o.totals.visitors} before={o.previousTotals.visitors} period={vs} note="Unieke bezoekers per dag, opgeteld" />
          <StatCard label="Paginaweergaven" value={o.totals.pageViews} before={o.previousTotals.pageViews} period={vs} />
          <StatCard label="Pagina's per bezoeker" value={o.totals.visitors ? Math.round((o.totals.pageViews / o.totals.visitors) * 10) / 10 : 0} period={vs} />
          <StatCard label="Binnenkomsten" value={landings} period={vs} note="Eerste pagina van een bezoek van buitenaf" />
        </div>
        <section className="panel">
          <TimeChart title="Bezoekers en paginaweergaven" bucket={o.bucket} dates={dates} series={[
            { key: "visitors", label: "Bezoekers", color: "var(--chart-1)", values: o.series.map((p) => p.visitors) },
            { key: "pageViews", label: "Paginaweergaven", color: "var(--chart-2)", values: o.series.map((p) => p.pageViews) },
          ]} />
        </section>
        <section className="panel stack">
          <h2>Bekeken pagina&apos;s</h2>
          <BarList total={o.pages.reduce((s, p) => s + p.views, 0)} items={o.pages.map((p) => ({ label: PAGE_LABEL[p.page] ?? p.page, value: p.views }))} empty="Nog geen paginaweergaven in deze periode." />
        </section>
      </>}

      {tab === "bronnen" && <div className="dash-grid">
        <section className="panel stack">
          <h2>Soort bron</h2>
          <BarList items={[...kinds].sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ label: REF_KIND_LABEL[k], value: v }))} empty="Nog geen binnenkomsten in deze periode." />
        </section>
        <section className="panel stack">
          <h2>Binnengekomen via domein</h2>
          <BarList items={o.entries.map((e) => ({ label: ENTRY_LABEL[e.entry] ?? e.entry, value: e.landings }))} empty="Nog geen binnenkomsten in deze periode." />
        </section>
        <section className="panel stack">
          <h2>Verwijzende sites</h2>
          <BarList items={o.referrers.map((r) => ({ label: r.referrer === "" ? "Direct of onbekend" : r.referrer === "*" ? "Overige sites" : r.referrer, value: r.landings }))} empty="Nog geen binnenkomsten in deze periode." />
        </section>
        <section className="panel"><p className="lead">Alleen de hostnaam van de verwijzende site wordt bewaard, nooit een pad of zoekterm. De telling per domein loopt via <code>?via=</code> op de doorverwijzing van kleurhoek.be en kleurhoek.com (ADR 0032).</p></section>
      </div>}

      {tab === "inhoud" && <>
        <div className="ui-stats dash-stats">
          <StatCard label="Platen bekeken" value={o.totals.plateViews} before={o.previousTotals.plateViews} period={vs} />
          <StatCard label="Geprint" value={o.totals.prints} before={o.previousTotals.prints} period={vs} />
          <StatCard label="Gedownload" value={o.totals.pdfDownloads} before={o.previousTotals.pdfDownloads} period={vs} />
          <StatCard label="Helemaal ingekleurd" value={o.totals.completions} before={o.previousTotals.completions} period={vs} note={`${pct(o.totals.completions, o.totals.plateViews)} van de bekeken platen`} />
          <StatCard label="'Wat heb je nodig' bekeken" value={o.totals.materialsViews} period={vs} />
          <StatCard label="Doorkliks naar winkels" value={o.totals.productClicks} period={vs} note={`${pct(o.totals.productClicks, o.totals.materialsViews)} klikratio`} />
        </div>
        <section className="panel">
          <h2>Populairste platen</h2>
          {o.topPlates.length === 0 ? <p className="lead">Nog geen platen bekeken in deze periode.</p> : (
            <table><thead><tr><th>Plaat</th><th className="num">Bekeken</th><th className="num">Downloads</th><th className="num">Prints</th><th className="num">Ingekleurd</th><th className="num">Gebruikt</th></tr></thead>
              <tbody>{o.topPlates.map((p) => <tr key={p.plate}><td>{p.plate}</td><td className="num">{num(p.views)}</td><td className="num">{num(p.downloads)}</td><td className="num">{num(p.prints)}</td><td className="num">{num(p.completions)}</td><td className="num">{pct(p.downloads + p.prints + p.completions, p.views)}</td></tr>)}</tbody></table>
          )}
          <p className="lead">"Gebruikt" = gedownload, geprint of helemaal ingekleurd, gedeeld door bekeken.</p>
        </section>
      </>}

      {tab === "techniek" && <section className="panel stack">
        <h2>Landen</h2>
        {o.countries.some((c) => c.country) ? <WorldMap items={o.countries.map((c) => ({ country: c.country, value: c.pageViews + c.plateViews }))} /> : <p className="lead">Nog geen bezoek met een bekend land in deze periode.</p>}
      </section>}
      {tab === "techniek" && <div className="dash-grid">
        <section className="panel stack"><h2>Apparaten</h2><BarList items={o.devices.map((d) => ({ label: DEVICE_LABEL[d.device] ?? d.device, value: d.views }))} /></section>
        <section className="panel stack"><h2>Ranglijst landen</h2><BarList items={o.countries.map((c) => ({ label: countryName(c.country), value: c.pageViews + c.plateViews }))} /></section>
        <section className="panel"><p className="lead">Browsers, schermformaten en besturingssystemen tellen we bewust niet: samen maken die een bezoeker herkenbaar (ADR 0002).</p></section>
      </div>}

      {tab === "organisaties" && <section className="panel">
        <h2>Per organisatie</h2>
        {o.organizations.length === 0 ? <p className="lead">Nog geen bezoeken in deze periode.</p> : (
          <table><thead><tr><th>Organisatie</th><th className="num">Bezoekers</th><th className="num">Paginaweergaven</th></tr></thead>
            <tbody>{o.organizations.map((x) => <tr key={x.org}><td>{orgNames.get(x.org) ?? x.org}</td><td className="num">{num(x.visitors)}</td><td className="num">{num(x.views)}</td></tr>)}</tbody></table>
        )}
      </section>}

      {tab === "nu" && live && <>
        <div className="ui-stats dash-stats">
          <StatCard label="Bezoekers, laatste 30 minuten" value={live.visitors} period="" />
          <StatCard label="Paginaweergaven, laatste 30 minuten" value={live.pageViews} period="" />
        </div>
        <div className="dash-grid">
          <section className="panel stack"><h2>Pagina&apos;s</h2><BarList items={live.pages.map((p) => ({ label: PAGE_LABEL[p.page] ?? p.page, value: p.views }))} empty="Op dit moment niemand op de site." /></section>
          <section className="panel stack"><h2>Platen</h2><BarList items={live.plates.map((p) => ({ label: p.plate, value: p.views }))} empty="Geen platen bekeken in de laatste 30 minuten." /></section>
        </div>
        <p className="lead">Ververs de pagina voor de nieuwste stand.</p>
      </>}
    </>
  );
}
