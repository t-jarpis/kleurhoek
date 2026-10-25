import { adminApi, describe, type MailSubscriber } from "@/lib/api";
import { removeSubscriber } from "./actions";
import { MailNav, TOPIC_LABEL } from "./nav";

export const metadata = { title: "Mail" };
export const dynamic = "force-dynamic";

/** Mail (ADR 0037): stand van versturen, abonnees per onderwerp en markt, de wachtrij, en één adres opzoeken. */
export default async function MailOverview({ searchParams }: { searchParams: Promise<{ melding?: string; email?: string }> }) {
  const { melding, email } = await searchParams;
  let data;
  try {
    const [overview, me] = await Promise.all([adminApi.mailOverview(), adminApi.me()]);
    const canManage = me.permissions.includes("mail.manage");
    const found: MailSubscriber | null | undefined = canManage && email ? await adminApi.mailSubscriber(email) : undefined;
    data = { overview, canManage, found };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { overview: o, canManage, found } = data;
  const off = !o.sending.bulk || !o.sending.transactional;
  return (
    <>
      <div>
        <h1>Mail</h1>
        <p className="lead">Mails aan abonnees: bevestigen, welkom, nieuwe platen, feestdagen en de nieuwsbrief. Abonnees melden zich aan op de site of in hun account; afmelden kan onder elke mail met één klik. Geen open- of kliktracking.</p>
      </div>
      <div className="toolbar"><MailNav active="overzicht" /></div>
      {melding && <p className="note" role="status">{melding}</p>}
      {off && (
        <div className="ui-callout" data-tone="warning"><p><strong>Versturen staat {o.sending.bulk || o.sending.transactional ? "deels " : ""}uit.</strong> {!o.sending.transactional && "Bevestigingsmails (MAIL_TRANSACTIONAL_SMTP_URL of MAIL_SMTP_URL) "}{!o.sending.transactional && !o.sending.bulk && "en "}{!o.sending.bulk && "nieuwsbrief en automatische mails (MAIL_SMTP_URL) "}gaan pas weg als er een SMTP-dienst is ingesteld. Tot die tijd wachten ze; na 3 dagen vervallen ze.</p></div>
      )}
      <div className="cards">
        <div className="ui-stat"><span>Abonnees</span><strong>{o.subscribers.active}</strong><small>{o.subscribers.pending} nog niet bevestigd</small></div>
        <div className="ui-stat"><span>Verstuurd (7 dagen)</span><strong>{o.queue.sent ?? 0}</strong><small>{o.queue.queued ?? 0} in de wachtrij</small></div>
        <div className="ui-stat"><span>Mislukt (7 dagen)</span><strong>{o.queue.failed ?? 0}</strong><small>{o.queue.expired ?? 0} vervallen of overgeslagen</small></div>
      </div>
      <section className="panel">
        <h2>Abonnees per onderwerp en markt</h2>
        <table>
          <thead><tr><th>Onderwerp</th><th className="num">Abonnees</th></tr></thead>
          <tbody>{o.options.topics.map((t) => <tr key={t}><td>{TOPIC_LABEL[t] ?? t}</td><td className="num">{o.subscribers.byTopic[t] ?? 0}</td></tr>)}</tbody>
        </table>
        <table>
          <thead><tr><th>Markt</th><th className="num">Abonnees</th></tr></thead>
          <tbody>{Object.entries(o.subscribers.byMarket).map(([m, n]) => <tr key={m}><td><code>{m}</code></td><td className="num">{n}</td></tr>)}</tbody>
        </table>
      </section>
      {o.queue.errors.length > 0 && (
        <section className="panel">
          <h2>Fouten bij versturen</h2>
          <table><thead><tr><th>Fout</th><th className="num">Aantal</th></tr></thead>
            <tbody>{o.queue.errors.map((e) => <tr key={e.error ?? ""}><td>{e.error ?? "—"}</td><td className="num">{e.n}</td></tr>)}</tbody></table>
        </section>
      )}
      {canManage && (
        <section className="panel stack">
          <h2>Abonnee opzoeken</h2>
          <p className="lead">Op exact e-mailadres, bijvoorbeeld voor een verzoek om gegevens te verwijderen. Er is bewust geen lijst om door te bladeren.</p>
          <form className="grid-form" method="get">
            <label className="field"><span>E-mailadres</span><input name="email" type="email" defaultValue={email ?? ""} autoComplete="off" required /></label>
            <div><button type="submit">Zoeken</button></div>
          </form>
          {found === null && <p className="lead">Geen abonnee met dit adres.</p>}
          {found && (
            <div className="stack">
              <dl className="facts">
                <dt>Adres</dt><dd>{found.email}</dd>
                <dt>Stand</dt><dd>{found.status === "active" ? "Actief" : "Nog niet bevestigd"}{found.viaAccount ? " (via account)" : ""}</dd>
                <dt>Onderwerpen</dt><dd>{found.topics.map((t) => TOPIC_LABEL[t] ?? t).join(", ")}</dd>
                <dt>Markt</dt><dd><code>{found.market}</code></dd>
                <dt>Aangemeld</dt><dd>{new Date(found.consentAt).toLocaleString("nl-NL", { dateStyle: "medium", timeStyle: "short" })}{found.confirmedAt ? `, bevestigd ${new Date(found.confirmedAt).toLocaleString("nl-NL", { dateStyle: "medium", timeStyle: "short" })}` : ""}</dd>
              </dl>
              <form action={removeSubscriber}><input type="hidden" name="id" value={found.id} /><button type="submit" className="danger">Verwijderen</button></form>
            </div>
          )}
        </section>
      )}
    </>
  );
}
