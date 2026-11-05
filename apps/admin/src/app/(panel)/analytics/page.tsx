import Link from "next/link";
import { ActivityHeatmap } from "@/components/charts/ActivityHeatmap";
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
const PAGE_LABEL: Record<string, string> = { home: "Home", plaat: "Plaatpagina's", boekje: "Boekje", account: "Account", "niet-gevonden": "Niet gevonden", disclaimer: "Disclaimer", contact: "Contact", themas: "Thema's", thema: "Themapagina's", "eigen-omgeving": "Eigen omgeving", onderwerp: "Onderwerppagina's", aftelkalender: "Aftelkalender", lespakket: "Lespakketten", samen: "Samen kleuren" };
const DEVICE_LABEL: Record<string, string> = { mobile: "Telefoon", tablet: "Tablet", desktop: "Computer", other: "Overig" };
const ENTRY_LABEL: Record<string, string> = { nl: "kleurhoek.nl", be: "kleurhoek.be", com: "kleurhoek.com" };
const iso = (d: Date) => d.toISOString().slice(0, 10);
/** Kwam binnen via (ADR 0083): "google.com → een plaat", "rechtstreeks → de voorpagina", of "—". */
const ONE_PAGE: Record<string, string> = { plaat: "een plaat", onderwerp: "een onderwerppagina", thema: "een themapagina", lespakket: "een lespakket", home: "de voorpagina" };
const viaText = (v: { referrer: string; page: string } | null | undefined) => (v ? `${v.referrer || "rechtstreeks"}${v.page ? ` → ${ONE_PAGE[v.page] ?? (PAGE_LABEL[v.page] ?? v.page).toLowerCase()}` : ""}` : "—");
/** Tijdstip in Nederlandse tijd: "di 3 nov 14:05". */
const when = (at: string) => new Intl.DateTimeFormat("nl-NL", { timeZone: "Europe/Amsterdam", weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(at));
const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 1000) / 10}%`.replace(".", ",") : "—");
const countryName = (code: string) => { try { return code ? new Intl.DisplayNames(["nl"], { type: "region" }).of(code) ?? code : "Onbekend"; } catch { return code || "Onbekend"; } };

export default async function Analytics({ searchParams }: { searchParams: Promise<{ tab?: string; periode?: string }> }) {
  const sp = await searchParams;
  const tab: Tab = TABS.some(([t]) => t === sp.tab) ? (sp.tab as Tab) : "bezoekers";
  const period: Period = PERIODS.some(([p]) => p === sp.periode) ? (sp.periode as Period) : "30";
  const to = new Date(), from = new Date(Date.now() - (Number(period) - 1) * 86_400_000);
  const href = (t: Tab, p: Period = period) => `/analytics?tab=${t}&periode=${p}`;
  let o, live, act, orgNames = new Map<string, string>();
  try {
    [o, live, act] = await Promise.all([adminApi.overview(iso(from), iso(to)), tab === "nu" ? adminApi.realtime() : Promise.resolve(null), tab === "inhoud" ? adminApi.activity(iso(from), iso(to)) : Promise.resolve(null)]);
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
          <StatCard label="Gedownload" value={o.totals.pdfDownloads} before={o.previousTotals.pdfDownloads} period={vs} note="Opgeslagen als afbeelding of filmpje" />
          <StatCard label="Gedeeld" value={o.totals.shares ?? 0} before={o.previousTotals.shares ?? 0} period={vs} note={`${num(o.totals.sharedVisits ?? 0)} bezoeken via een gedeelde link`} />
          <StatCard label="Online gekleurd" value={o.totals.colored ?? 0} before={o.previousTotals.colored ?? 0} period={vs} note={`${pct(o.totals.colored ?? 0, o.totals.plateViews)} van de bekeken platen, ook deels`} />
          <StatCard label="Af met kleur op nummer" value={o.totals.completions} before={o.previousTotals.completions} period={vs} />
          <StatCard label="'Wat heb je nodig' bekeken" value={o.totals.materialsViews} period={vs} />
          <StatCard label="Doorkliks naar winkels" value={o.totals.productClicks} period={vs} note={`${pct(o.totals.productClicks, o.totals.materialsViews)} klikratio`} />
        </div>
        <section className="panel">
          <h2>Populairste platen</h2>
          {o.topPlates.length === 0 ? <p className="lead">Nog geen platen bekeken in deze periode.</p> : (
            <table><thead><tr><th>Plaat</th><th className="num">Bekeken</th><th className="num">Downloads</th><th className="num">Prints</th><th className="num">Gekleurd</th><th className="num">Gedeeld</th><th className="num">Gebruikt</th></tr></thead>
              <tbody>{o.topPlates.map((p) => <tr key={p.plate}><td>{p.plate}</td><td className="num">{num(p.views)}</td><td className="num">{num(p.downloads)}</td><td className="num">{num(p.prints)}</td><td className="num">{num(p.colored ?? 0)}</td><td className="num">{num(p.shares ?? 0)}</td><td className="num">{pct(p.downloads + p.prints + (p.colored ?? 0), p.views)}</td></tr>)}</tbody></table>
          )}
          <p className="lead">"Gekleurd" = online begonnen met kleuren, ook als het niet af is. "Gebruikt" = gedownload, geprint of online gekleurd, gedeeld door bekeken.</p>
        </section>
        {act && <section className="panel">
          <h2>Wanneer wordt er gedownload en geprint?</h2>
          <p className="lead">Per weekdag en uur, Nederlandse tijd{act.limited ? `, vanaf ${act.from} (oudere tijdstippen bewaren we niet; de totalen hierboven gaan wel over de hele periode)` : ""}.</p>
          <ActivityHeatmap grid={act.grid} caption="Downloads en prints per weekdag en uur" />
          <h3>Laatste downloads en prints</h3>
          {act.latest.length === 0 ? <p className="lead">Nog geen downloads of prints in deze periode.</p> : (
            <table><thead><tr><th>Tijdstip</th><th>Wat</th><th>Plaat</th><th>Markt</th><th>Apparaat</th><th>Kwam binnen via</th></tr></thead>
              <tbody>{act.latest.map((e, i) => <tr key={`${e.at}-${i}`}><td>{when(e.at)}</td><td>{e.type === "print" ? "Geprint" : "Gedownload"}</td><td>{e.plate || "—"}</td><td>{e.market}</td><td>{DEVICE_LABEL[e.device] ?? e.device}</td><td>{viaText(e.via)}</td></tr>)}</tbody></table>
          )}
        </section>}
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
