import { GoalCard } from "@/components/charts/GoalCard";
import { longDate } from "@/components/charts/format";
import { TimeChart } from "@/components/charts/TimeChart";
import { adminApi, describe, type GoalMetric } from "@/lib/api";
import { saveGoals } from "./actions";

export const dynamic = "force-dynamic";
export const metadata = { title: "Doelen" };

const META: Record<GoalMetric, { label: string; card: string; unit: string; cumulative: boolean }> = {
  visits: { label: "Bezoeken per maand", card: "Bezoeken", unit: "bezoeken", cumulative: false },
  plates: { label: "Platen online", card: "Platen online", unit: "platen", cumulative: true },
  clicks: { label: "Doorkliks naar winkels per maand", card: "Doorkliks naar winkels", unit: "doorkliks", cumulative: false },
};
const ROWS = 6;

export default async function Goals({ searchParams }: { searchParams: Promise<{ melding?: string; bewerk?: string }> }) {
  const { melding, bewerk } = await searchParams;
  let g, me;
  try { [g, me] = await Promise.all([adminApi.goals(), adminApi.me().catch(() => null)]); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const canEdit = me?.permissions.includes("analytics.goals.manage") ?? false;
  const startText = longDate(`${g.start}-01`, "month");

  return (
    <>
      <div>
        <h1>Doelen</h1>
        <p className="lead">Waar we naartoe werken, per maand vanaf {startText}. Het doel is realistisch voor een nieuwe kleurplatensite in Nederland; de ambitie is wat kan als het meezit. Tussen de tussendoelen loopt de lijn recht.{g.custom ? "" : " Dit zijn de startwaarden; pas ze hieronder aan."}</p>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}

      <div className="ui-stats dash-stats">
        {g.metrics.map((m) => m.now && <GoalCard key={m.metric} label={META[m.metric].card} cumulative={META[m.metric].cumulative} {...m.now} />)}
      </div>

      {g.metrics.map((m) => (
        <section key={m.metric} className="panel">
          <TimeChart title={META[m.metric].label} bucket="month" dates={m.months.map((x) => `${x.month}-01`)} series={[
            { key: "actual", label: "Werkelijk", color: "var(--chart-1)", values: m.months.map((x) => x.actual) },
            { key: "target", label: "Doel", color: "var(--chart-2)", values: m.months.map((x) => x.target), dash: "dash" },
            { key: "stretch", label: "Ambitie", color: "var(--chart-3)", values: m.months.map((x) => x.stretch), dash: "dot" },
          ]} />
        </section>
      ))}

      <section className="panel">
        <h2>Doelen aanpassen</h2>
        {!canEdit ? <p className="lead">Alleen wie doelen mag wijzigen kan dit aanpassen.</p> : bewerk === undefined ? (
          <p><a href="/doelen?bewerk=1">Startmaand en tussendoelen aanpassen</a></p>
        ) : (
          <form action={saveGoals} className="goals-form">
            <label className="field"><span>Startmaand</span><input type="month" name="start" defaultValue={g.start} required /></label>
            {g.metrics.map((m) => (
              <fieldset key={m.metric}>
                <legend>{META[m.metric].label}</legend>
                <table>
                  <thead><tr><th>Maanden na de start</th><th className="num">Doel</th><th className="num">Ambitie</th></tr></thead>
                  <tbody>{Array.from({ length: ROWS }, (_, i) => {
                    const r = m.milestones[i];
                    const name = (k: string) => `${m.metric}.${i}.${k}`;
                    const aria = (k: string) => `${META[m.metric].label}, rij ${i + 1}: ${k}`;
                    return (
                      <tr key={i}>
                        <td><input type="number" min={0} max={60} name={name("month")} defaultValue={r?.month} aria-label={aria("maanden na de start")} /></td>
                        <td className="num"><input type="number" min={0} name={name("target")} defaultValue={r?.target} aria-label={aria("doel")} /></td>
                        <td className="num"><input type="number" min={0} name={name("stretch")} defaultValue={r?.stretch} aria-label={aria("ambitie")} /></td>
                      </tr>
                    );
                  })}</tbody>
                </table>
              </fieldset>
            ))}
            <p className="lead">Lege rijen tellen niet mee. Een lege ambitie is gelijk aan het doel.</p>
            <div className="row"><button type="submit">Opslaan</button> <a href="/doelen">Annuleren</a></div>
          </form>
        )}
      </section>
    </>
  );
}
