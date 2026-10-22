import { adminApi } from "@/lib/api";

export const dynamic = "force-dynamic";

const iso = (d: Date) => d.toISOString().slice(0, 10);

export default async function Dashboard() {
  const to = new Date(), from = new Date(Date.now() - 6 * 86_400_000);
  let data;
  try {
    const [summary, rules] = await Promise.all([adminApi.summary(iso(from), iso(to)), adminApi.rateLimits()]);
    data = { summary, rules };
  } catch (e) {
    return <div className="err"><h1>Geen verbinding met de API</h1><p>{(e as Error).message}</p></div>;
  }
  const { summary, rules } = data;
  const sum = (k: "pageViews" | "plateViews") => summary.byCountry.reduce((s, r) => s + r[k], 0);
  const blocked = rules.reduce((s, r) => s + r.days.reduce((t, d) => t + d.blocked, 0), 0);
  const downloads = summary.topPlates.reduce((s, r) => s + r.downloads + r.prints, 0);
  return (
    <>
      <div><h1>Dashboard</h1><p className="lead">Laatste 7 dagen, {iso(from)} t/m {iso(to)}. Tellingen zonder cookies of persoonsgegevens.</p></div>
      <div className="cards">
        <div className="stat"><span>Paginaweergaven</span><b>{sum("pageViews").toLocaleString("nl-NL")}</b></div>
        <div className="stat"><span>Platen bekeken</span><b>{sum("plateViews").toLocaleString("nl-NL")}</b></div>
        <div className="stat"><span>Downloads en prints</span><b>{downloads.toLocaleString("nl-NL")}</b></div>
        <div className="stat"><span>Geblokkeerde verzoeken</span><b className={blocked ? "bad" : ""}>{blocked.toLocaleString("nl-NL")}</b></div>
      </div>
      <section className="panel">
        <h2>Populairste platen</h2>
        {summary.topPlates.length === 0 ? <p className="lead">Nog geen downloads of prints in deze periode.</p> : (
          <table><thead><tr><th>Plaat</th><th className="num">Bekeken</th><th className="num">Downloads</th><th className="num">Prints</th><th className="num">Voltooid</th></tr></thead>
            <tbody>{summary.topPlates.map((p) => <tr key={p.plate}><td>{p.plate}</td><td className="num">{p.views}</td><td className="num">{p.downloads}</td><td className="num">{p.prints}</td><td className="num">{p.completions}</td></tr>)}</tbody></table>
        )}
      </section>
      <section className="panel">
        <h2>Bezoekers per land</h2>
        {summary.byCountry.length === 0 ? <p className="lead">Nog geen bezoeken in deze periode.</p> : (
          <table><thead><tr><th>Land</th><th className="num">Paginaweergaven</th><th className="num">Platen bekeken</th></tr></thead>
            <tbody>{summary.byCountry.map((c) => <tr key={c.country || "?"}><td>{c.country || "Onbekend"}</td><td className="num">{c.pageViews}</td><td className="num">{c.plateViews}</td></tr>)}</tbody></table>
        )}
        <p className="lead">Dagtotalen worden elke 10 minuten bijgewerkt.</p>
      </section>
    </>
  );
}
