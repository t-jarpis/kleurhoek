import Link from "next/link";
import { num } from "@/components/charts/format";
import { StatCard } from "@/components/charts/StatCard";
import { TimeChart } from "@/components/charts/TimeChart";
import { adminApi, describe } from "@/lib/api";

export const dynamic = "force-dynamic";
export const metadata = { title: "Dashboard" };

const PERIODS = [["7", "7 dagen"], ["30", "30 dagen"], ["90", "90 dagen"], ["365", "12 maanden"]] as const;
type Period = (typeof PERIODS)[number][0];
const PERIOD_TEXT: Record<Period, string> = { "7": "vorige 7 dagen", "30": "vorige 30 dagen", "90": "vorige 90 dagen", "365": "vorige 12 maanden" };
const iso = (d: Date) => d.toISOString().slice(0, 10);

export default async function Dashboard({ searchParams }: { searchParams: Promise<{ periode?: string }> }) {
  const raw = (await searchParams).periode;
  const period: Period = PERIODS.some(([p]) => p === raw) ? (raw as Period) : "30";
  const to = new Date(), from = new Date(Date.now() - (Number(period) - 1) * 86_400_000);
  let o, accounts, rules;
  try {
    [o, accounts, rules] = await Promise.all([adminApi.overview(iso(from), iso(to)), adminApi.accountStats(iso(from), iso(to)), adminApi.rateLimits().catch(() => [])]);
  } catch (e) {
    const d = describe(e);
    return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>;
  }
  const vs = PERIOD_TEXT[period];
  const blocked = rules.reduce((s, r) => s + r.days.reduce((t, d) => t + d.blocked, 0), 0);
  const dates = o.series.map((p) => p.date);
  const created = new Map(accounts.series.map((s) => [s.date, s.count]));

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

      <section className="panel">
        <h2>Meer cijfers</h2>
        <p className="lead">Pagina&apos;s, bronnen (domein en verwijzende sites), platen, apparaten, landen, organisaties en wie er nu op de site is staan onder <Link href={`/analytics?periode=${period}`}>Analytics</Link>.</p>
        <p className="lead">Terugkerende anonieme bezoekers tellen we niet: dat kan alleen door een browser te herkennen, en dat doen we niet (ADR 0002). Terugkerende accounts zijn accounts van vóór de periode die erin inlogden. Geblokkeerde verzoeken (rate limits): {num(blocked)}.</p>
      </section>
    </>
  );
}
