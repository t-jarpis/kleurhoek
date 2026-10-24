import Link from "next/link";
import { BarList } from "@/components/charts/BarList";
import { num } from "@/components/charts/format";
import { StatCard } from "@/components/charts/StatCard";
import { TimeChart } from "@/components/charts/TimeChart";
import { adminApi, describe } from "@/lib/api";

export const dynamic = "force-dynamic";
export const metadata = { title: "Dashboard" };

const PERIODS = [["7", "7 dagen"], ["30", "30 dagen"], ["90", "90 dagen"], ["365", "12 maanden"]] as const;
type Period = (typeof PERIODS)[number][0];
const PERIOD_TEXT: Record<Period, string> = { "7": "vorige 7 dagen", "30": "vorige 30 dagen", "90": "vorige 90 dagen", "365": "vorige 12 maanden" };
const PAGE_LABEL: Record<string, string> = { home: "Home", plaat: "Plaatpagina's", boekje: "Boekje", account: "Account" };
const DEVICE_LABEL: Record<string, string> = { mobile: "Telefoon", tablet: "Tablet", desktop: "Computer", other: "Overig" };
const ENTRY_LABEL: Record<string, string> = { nl: "kleurhoek.nl", be: "kleurhoek.be", com: "kleurhoek.com" };
const refLabel = (r: string) => (r === "" ? "Direct of onbekend" : r === "*" ? "Overige sites" : r);
const iso = (d: Date) => d.toISOString().slice(0, 10);
const countryName = (code: string) => { try { return code ? new Intl.DisplayNames(["nl"], { type: "region" }).of(code) ?? code : "Onbekend"; } catch { return code || "Onbekend"; } };

export default async function Dashboard({ searchParams }: { searchParams: Promise<{ periode?: string }> }) {
  const raw = (await searchParams).periode;
  const period: Period = PERIODS.some(([p]) => p === raw) ? (raw as Period) : "30";
  const to = new Date(), from = new Date(Date.now() - (Number(period) - 1) * 86_400_000);
  let o, accounts, rules, orgNames = new Map<string, string>();
  try {
    [o, accounts, rules] = await Promise.all([adminApi.overview(iso(from), iso(to)), adminApi.accountStats(iso(from), iso(to)), adminApi.rateLimits().catch(() => [])]);
    orgNames = new Map((await adminApi.organizations().catch(() => ({ organizations: [] as { slug: string; name: string }[] }))).organizations.map((x) => [x.slug, x.name]));
  } catch (e) {
    const d = describe(e);
    return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>;
  }
  const vs = PERIOD_TEXT[period];
  const blocked = rules.reduce((s, r) => s + r.days.reduce((t, d) => t + d.blocked, 0), 0);
  const dates = o.series.map((p) => p.date);
  const created = new Map(accounts.series.map((s) => [s.date, s.count]));
  const pageTotal = o.pages.reduce((s, p) => s + p.views, 0);

  return (
    <>
      <div className="row-between dash-head">
        <div><h1>Dashboard</h1><p className="lead">{o.from} t/m {o.to}, per {o.bucket === "week" ? "week" : "dag"}. Tellingen zonder cookies of persoonsgegevens; bijgewerkt elke 10 minuten.</p></div>
        <nav className="tabs" aria-label="Periode">
          {PERIODS.map(([p, label]) => <Link key={p} href={`/?periode=${p}`} aria-current={p === period ? "page" : undefined}>{label}</Link>)}
        </nav>
      </div>

      <div className="ui-stats dash-stats">
        <StatCard label="Bezoekers" value={o.totals.visitors} before={o.previousTotals.visitors} period={vs} note="Unieke bezoekers per dag, opgeteld" />
        <StatCard label="Paginaweergaven" value={o.totals.pageViews} before={o.previousTotals.pageViews} period={vs} />
        <StatCard label="Downloads en prints" value={o.totals.downloads} before={o.previousTotals.downloads} period={vs} />
        <StatCard label="Platen ingekleurd" value={o.totals.completions} before={o.previousTotals.completions} period={vs} />
        <StatCard label="Nieuwe accounts" value={accounts.created} before={accounts.createdBefore} period={vs} note={`${num(accounts.total)} accounts in totaal`} />
        <StatCard label="Terugkerende accounts" value={accounts.returning} period={vs} note={`${num(accounts.active)} accounts logden in deze periode in`} />
      </div>

      <section className="panel">
        <TimeChart title="Bezoekers en paginaweergaven" bucket={o.bucket} dates={dates} series={[
          { key: "visitors", label: "Bezoekers", color: "var(--chart-1)", values: o.series.map((p) => p.visitors) },
          { key: "pageViews", label: "Paginaweergaven", color: "var(--chart-2)", values: o.series.map((p) => p.pageViews) },
        ]} />
      </section>

      <div className="dash-grid">
        <section className="panel">
          <TimeChart title="Downloads en prints" kind="bar" bucket={o.bucket} dates={dates} series={[
            { key: "downloads", label: "Downloads en prints", color: "var(--chart-3)", values: o.series.map((p) => p.downloads) },
          ]} />
        </section>
        <section className="panel">
          <TimeChart title="Nieuwe accounts" kind="bar" bucket={o.bucket} dates={dates} series={[
            { key: "accounts", label: "Nieuwe accounts", color: "var(--chart-4)", values: dates.map((d) => created.get(d) ?? 0) },
          ]} />
        </section>
      </div>

      <div className="dash-grid">
        <section className="panel stack">
          <h2>Bekeken pagina&apos;s</h2>
          <BarList total={pageTotal} items={o.pages.map((p) => ({ label: PAGE_LABEL[p.page] ?? p.page, value: p.views }))}
            empty="Nog geen paginaweergaven. Pagina's worden geteld sinds 24 oktober 2026." />
        </section>
        <section className="panel stack">
          <h2>Populairste platen</h2>
          <BarList items={o.topPlates.filter((p) => p.views > 0).map((p) => ({ label: p.plate, value: p.views }))} empty="Nog geen platen bekeken in deze periode." />
        </section>
        <section className="panel stack">
          <h2>Apparaten</h2>
          <BarList items={o.devices.map((d) => ({ label: DEVICE_LABEL[d.device] ?? d.device, value: d.views }))} />
        </section>
        <section className="panel stack">
          <h2>Landen</h2>
          <BarList items={o.countries.map((c) => ({ label: countryName(c.country), value: c.pageViews + c.plateViews }))} />
        </section>
        <section className="panel stack">
          <h2>Binnengekomen via domein</h2>
          <BarList items={o.entries.map((e) => ({ label: ENTRY_LABEL[e.entry] ?? e.entry, value: e.landings }))} empty="Nog geen binnenkomsten in deze periode." />
        </section>
        <section className="panel stack">
          <h2>Verwijzende sites</h2>
          <BarList items={o.referrers.map((r) => ({ label: refLabel(r.referrer), value: r.landings }))} empty="Nog geen binnenkomsten in deze periode." />
        </section>
      </div>

      {o.organizations.length > 1 && (
        <section className="panel">
          <h2>Per organisatie</h2>
          <table>
            <thead><tr><th>Organisatie</th><th className="num">Bezoekers</th><th className="num">Paginaweergaven</th></tr></thead>
            <tbody>{o.organizations.map((x) => <tr key={x.org}><td>{orgNames.get(x.org) ?? x.org}</td><td className="num">{num(x.visitors)}</td><td className="num">{num(x.views)}</td></tr>)}</tbody>
          </table>
        </section>
      )}

      <section className="panel">
        <h2>Populairste platen in detail</h2>
        {o.topPlates.length === 0 ? <p className="lead">Nog geen platen bekeken in deze periode.</p> : (
          <table><thead><tr><th>Plaat</th><th className="num">Bekeken</th><th className="num">Downloads</th><th className="num">Prints</th><th className="num">Ingekleurd</th></tr></thead>
            <tbody>{o.topPlates.map((p) => <tr key={p.plate}><td>{p.plate}</td><td className="num">{num(p.views)}</td><td className="num">{num(p.downloads)}</td><td className="num">{num(p.prints)}</td><td className="num">{num(p.completions)}</td></tr>)}</tbody></table>
        )}
        <p className="lead">Terugkerende anonieme bezoekers tellen we niet: dat kan alleen door een browser te herkennen, en dat doen we niet (ADR 0002). Terugkerende accounts zijn accounts van vóór de periode die erin inlogden. Geblokkeerde verzoeken (rate limits): {num(blocked)}.</p>
      </section>
    </>
  );
}
