import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { deleteWorkflow } from "../actions";
import { MailNav } from "../nav";
import { describeStep, describeTrigger } from "./labels";

export const metadata = { title: "Workflows · Mail" };
export const dynamic = "force-dynamic";

/** Workflows (ADR 0037): aanleiding en stappen. Elke abonnee krijgt per aanleiding hooguit één keer dezelfde mail. */
export default async function Workflows({ searchParams }: { searchParams: Promise<{ melding?: string }> }) {
  const { melding } = await searchParams;
  let data;
  try {
    const [list, me] = await Promise.all([adminApi.mailWorkflows(), adminApi.me()]);
    data = { ...list, canManage: me.permissions.includes("mail.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { workflows, runs, options, canManage } = data;
  const names = new Map(options.templates.map((t) => [t.slug, t.name]));
  return (
    <>
      <div><h1>Workflows</h1><p className="lead">Automatische mails: een aanleiding (na aanmelden, een vaste dag, nieuwe platen, een feestdag die eraan komt) en daarna stappen. Lopend en afgerond over de laatste 30 dagen.</p></div>
      <div className="toolbar"><MailNav active="workflows" />{canManage && <Link className="ui-btn" data-variant="primary" href="/mail/workflows/nieuw">Nieuwe workflow</Link>}</div>
      {melding && <p className="note" role="status">{melding}</p>}
      <section className="panel">
        <table>
          <thead><tr><th>Naam</th><th>Stand</th><th>Aanleiding</th><th>Stappen</th><th className="num">Lopend</th><th className="num">Afgerond</th><th><span className="visually-hidden">Acties</span></th></tr></thead>
          <tbody>{workflows.map((w) => (
            <tr key={w.slug}>
              <td><Link href={`/mail/workflows/${w.slug}`}>{w.name}</Link></td>
              <td><span className="ui-badge" data-tone={w.enabled ? "success" : "warning"}>{w.enabled ? "Actief" : "Uit"}</span></td>
              <td>{describeTrigger(w.trigger)}</td>
              <td><ol style={{ margin: 0, paddingInlineStart: "1.2em" }}>{w.steps.map((s, i) => <li key={i}>{describeStep(s, names)}</li>)}</ol></td>
              <td className="num">{runs[w.slug]?.waiting ?? 0}</td>
              <td className="num">{(runs[w.slug]?.done ?? 0) + (runs[w.slug]?.stopped ?? 0)}</td>
              <td>{canManage && <form action={deleteWorkflow}><input type="hidden" name="slug" value={w.slug} /><button type="submit" className="ghost">Verwijderen<span className="visually-hidden"> {w.name}</span></button></form>}</td>
            </tr>
          ))}</tbody>
        </table>
      </section>
    </>
  );
}
