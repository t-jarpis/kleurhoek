import Link from "next/link";
import { adminApi, describe, type ConversationStatus } from "@/lib/api";
import { CHANNEL_LABEL, ContactNav, STATUS_LABEL, TOPIC_LABEL, when } from "./labels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Contact" };

const FILTERS: (ConversationStatus | "alles")[] = ["new", "open", "answered", "closed", "alles"];

/** Inbox (ADR 0023): berichten van het contactformulier, later ook WhatsApp. */
export default async function ContactInbox({ searchParams }: { searchParams: Promise<{ status?: string; pagina?: string; melding?: string; fout?: string }> }) {
  const q = await searchParams;
  const status = (["new", "open", "answered", "closed"] as const).find((s) => s === q.status) ?? (q.status === "alles" ? undefined : "new");
  const page = Math.max(1, Number(q.pagina) || 1);
  let inbox;
  try { inbox = await adminApi.inbox({ ...(status ? { status } : {}), page }); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const current = status ?? "alles";
  const pages = Math.max(1, Math.ceil(inbox.total / inbox.pageSize));
  return (
    <>
      <div className="row-between">
        <div><h1>Contact</h1><p className="lead">Berichten via de website. Persoonsgegevens worden na 12 maanden vanzelf verwijderd.</p></div>
        <ContactNav active="inbox" unread={inbox.counts.new} />
      </div>
      {q.melding && <p className="note" role="status">{q.melding}</p>}
      {q.fout && <div className="err" role="alert"><p>{q.fout}</p></div>}
      <nav className="tabs" aria-label="Status">
        {FILTERS.map((f) => (
          <Link key={f} href={`/contact?status=${f}`} aria-current={current === f ? "page" : undefined}>
            {f === "alles" ? "Alles" : `${STATUS_LABEL[f]} (${inbox.counts[f]})`}
          </Link>
        ))}
      </nav>
      <section className="panel">
        {inbox.conversations.length === 0 ? <p className="lead">Geen berichten in deze lijst.</p> : (
          <table>
            <thead><tr><th>Ontvangen</th><th>Van en bericht</th><th>Onderwerp</th><th>Status</th></tr></thead>
            <tbody>
              {inbox.conversations.map((c) => (
                <tr key={c.id} className="ui-inbox-row" data-unread={c.status === "new"}>
                  <td>{when(c.lastMessageAt)}</td>
                  <td><Link href={`/contact/${c.id}`}>{c.name ?? c.email ?? c.phone ?? "Onbekend"}</Link><span className="ui-inbox-preview">{c.preview}</span></td>
                  <td>{TOPIC_LABEL[c.topic]}<span className="ui-inbox-preview">{CHANNEL_LABEL[c.channel]} · {c.org} · {c.market}</span></td>
                  <td><span className={`pill ${c.status === "new" || c.status === "open" ? "on" : "off"}`}>{STATUS_LABEL[c.status]}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {pages > 1 && (
          <div className="pager">
            {page > 1 && <Link href={`/contact?status=${current}&pagina=${page - 1}`}>← Vorige</Link>}
            <span>Pagina {page} van {pages}</span>
            {page < pages && <Link href={`/contact?status=${current}&pagina=${page + 1}`}>Volgende →</Link>}
          </div>
        )}
      </section>
    </>
  );
}
