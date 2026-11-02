import Link from "next/link";
import { adminApi, describe, type Change } from "@/lib/api";
import { undoChange } from "./actions";

export const dynamic = "force-dynamic";
export const metadata = { title: "Wijzigingen" };

const when = (iso: string) => new Date(iso).toLocaleString("nl-NL", { timeZone: "Europe/Amsterdam", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
const what = (c: Change) => (c.action.startsWith("undo:") ? `Ongedaan gemaakt: ${c.action.slice(5)}` : c.label ?? c.action);
const json = (v: unknown) => JSON.stringify(v, null, 2) ?? "—";

/** Wijzigingen (ADR 0066): het auditlog, met ongedaan maken voor de laatste wijziging van iets. */
export default async function Changes({ searchParams }: { searchParams: Promise<{ voor?: string; m?: string }> }) {
  const { voor, m } = await searchParams;
  let items: Change[];
  try { items = await adminApi.changes(voor); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const last = items.at(-1);
  return (
    <>
      <div><h1>Wijzigingen</h1><p className="lead">Wat beheerders en het systeem hebben gewijzigd, nieuwste eerst. De laatste wijziging van iets kun je terugzetten als je daar het recht voor hebt; het terugzetten komt zelf ook in deze lijst.</p></div>
      {m && <div role="status" className="ui-callout" data-tone={m.startsWith("fout:") ? "danger" : "success"}>{m.startsWith("fout:") ? m.slice(5) : "Teruggezet."}</div>}
      <section className="panel ui-changes">
        <table>
          <thead><tr><th>Wanneer</th><th>Door</th><th>Wat</th><th>Waarop</th><th>Ongedaan maken</th></tr></thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.id}>
                <td>{when(c.at)}</td>
                <td>{c.actor}</td>
                <td>
                  <b>{what(c)}</b>
                  <details><summary className="lead">Voor en na</summary><pre>{`Voor:\n${json(c.before)}\n\nNa:\n${json(c.after)}`}</pre></details>
                </td>
                <td><code>{c.subject}</code></td>
                <td className="status">
                  {c.undo === "ja" ? (
                    <form action={undoChange} className="inline"><input type="hidden" name="id" value={c.id} /><button type="submit" className="ghost">Terugzetten</button></form>
                  ) : <span className="lead">{c.undo === "verouderd" ? "Later nog gewijzigd" : c.undo === "geen-recht" ? "Geen recht" : "—"}</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 50 && last && <p><Link href={`/wijzigingen?voor=${encodeURIComponent(last.at)}`}>Oudere wijzigingen</Link></p>}
      </section>
    </>
  );
}
