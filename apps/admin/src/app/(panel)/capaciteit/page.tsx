import { TimeChart } from "@/components/charts/TimeChart";
import { adminApi, describe, type CapacityApp } from "@/lib/api";

export const dynamic = "force-dynamic";
export const metadata = { title: "Capaciteit" };

const NAMES: Record<string, string> = { web: "Website", api: "API", admin: "Beheer", login: "Inloggen" };
const ADVICE = { omlaag: ["Kan kleiner", "accent"], goed: ["Past", "success"], omhoog: ["Groter maken", "warning"], onbekend: ["Nog te weinig cijfers", undefined] } as const;
const nl = (n: number, d = 0) => n.toLocaleString("nl-NL", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (v: number | null) => (v === null ? "–" : `${nl(v)} %`);
const euro = (n: number) => n.toLocaleString("nl-NL", { style: "currency", currency: "EUR" });
const size = (a: CapacityApp) => `${nl(a.cpu / 1000, 2)} vCPU · ${a.memory >= 1024 ? `${nl(a.memory / 1024)} GB` : `${a.memory} MB`} · ${a.min} tot ${a.max} ${a.max === 1 ? "exemplaar" : "exemplaren"}`;

/** Capaciteit van de servers (ADR 0092): drukte per container met een advies. Schalen gebeurt in Terraform. */
export default async function Capaciteit() {
  let data;
  try { data = await adminApi.capacity(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const days = [...new Set([...data.apps.flatMap((a) => a.days.map((d) => d.day)), ...data.speed.map((s) => s.day)])].sort();
  const total = data.apps.reduce((t, a) => t + a.monthlyBase, 0);

  return (
    <>
      <div>
        <h1>Capaciteit</h1>
        <p className="lead">Hoe druk de servers het hebben en of ze groter of kleiner kunnen, op basis van de laatste zeven dagen. Dit is een advies: de maat zelf staat in Terraform (<code>infra/envs/prod/main.tf</code>).</p>
      </div>

      {!data.configured && (
        <div className="ui-callout" data-tone="warning" role="status">
          <p>De cijfers van Scaleway Cockpit zijn hier nog niet gekoppeld. Alleen de snelheidsmetingen lopen al. Na de koppeling (Terraform voor prod) verschijnen processor en geheugen vanzelf.</p>
        </div>
      )}

      {data.apps.length > 0 && (
        <section className="panel">
          <h2>Per container</h2>
          <p className="lead">Processor en geheugen: de drukste 5 % van de week, als deel van de maat. Vaste kosten samen: ± {euro(total)} per maand (zonder gratis tegoed).</p>
          <div className="ui-capacity-grid">{data.apps.map((a) => <Card key={a.app} a={a} />)}</div>
        </section>
      )}

      {data.apps.some((a) => a.days.length > 0) && (
        <section className="panel">
          <h2>Verloop</h2>
          <TimeChart title="Processor op drukke momenten (%)" dates={days} bucket="day" series={data.apps.map((a, i) => ({ key: a.app, label: NAMES[a.app] ?? a.app, color: `var(--chart-${(i % 5) + 1})`, values: days.map((d) => a.days.find((x) => x.day === d)?.cpuP95 ?? null) }))} />
          <TimeChart title="Geheugen op drukke momenten (%)" dates={days} bucket="day" series={data.apps.map((a, i) => ({ key: a.app, label: NAMES[a.app] ?? a.app, color: `var(--chart-${(i % 5) + 1})`, values: days.map((d) => a.days.find((x) => x.day === d)?.memP95 ?? null) }))} />
        </section>
      )}

      <section className="panel">
        <h2>Snelheid voor bezoekers</h2>
        <p className="lead">Elk kwartier vraagt de API een paar pagina&apos;s op zoals een bezoeker dat doet, via Cloudflare. Tijd tot het eerste antwoord; 95 % van de metingen was sneller dan de streepjeslijn.{data.speedP95 !== null && <> Deze week op z&apos;n traagst: {nl(data.speedP95)} ms.</>}</p>
        {data.speed.length === 0 ? (
          <p className="lead">Nog geen metingen. De eerste verschijnt binnen een kwartier na de uitrol.</p>
        ) : (
          data.paths.map((p, i) => (
            <TimeChart key={p} title={`Snelheid van ${p} (ms)`} dates={days} bucket="day" series={[
              { key: "p50", label: "Meestal", color: `var(--chart-${(i % 5) + 1})`, values: days.map((d) => data.speed.find((s) => s.day === d && s.path === p)?.p50 ?? null) },
              { key: "p95", label: "Traagste 5 %", color: `var(--chart-${(i % 5) + 1})`, dash: "dash", values: days.map((d) => data.speed.find((s) => s.day === d && s.path === p)?.p95 ?? null) },
            ]} />
          ))
        )}
        {data.speed.some((s) => s.failed > 0) && (
          <p className="lead">Mislukte metingen: {data.speed.filter((s) => s.failed > 0).map((s) => `${s.day} ${s.path} (${s.failed} van ${s.total})`).join(", ")}.</p>
        )}
      </section>
    </>
  );
}

/** CapacityCard uit het design system (ADR 0092). */
function Card({ a }: { a: CapacityApp }) {
  const week = a.days.slice(-7);
  const peak = (k: "cpuP95" | "memP95") => { const v = week.map((d) => d[k]).filter((x): x is number => x !== null); return v.length ? Math.max(...v) : null; };
  const cpu = peak("cpuP95"), mem = peak("memP95");
  const inst = Math.max(0, ...week.map((d) => d.instancesMax ?? 0));
  const [label, tone] = ADVICE[a.advice];
  return (
    <article className="ui-capacity">
      <header><h3>{NAMES[a.app] ?? a.app}</h3><small>{size(a)}</small></header>
      <dl>
        <div><dt>Processor</dt><dd><meter min={0} max={100} low={50} high={80} optimum={0} value={cpu ?? 0}>{pct(cpu)}</meter><span>{pct(cpu)}</span></dd></div>
        <div><dt>Geheugen</dt><dd><meter min={0} max={100} low={50} high={80} optimum={0} value={mem ?? 0}>{pct(mem)}</meter><span>{pct(mem)}</span></dd></div>
      </dl>
      <span className="ui-badge" data-tone={tone}>{label}</span>
      <p>{a.reason}</p>
      <footer>{a.min === 0 ? "Geen vaste kosten · schaalt naar nul" : `± ${euro(a.monthlyBase)} per maand vast`}{week.length > 0 && ` · hoogstens ${inst} ${inst === 1 ? "exemplaar" : "exemplaren"}`}</footer>
    </article>
  );
}
