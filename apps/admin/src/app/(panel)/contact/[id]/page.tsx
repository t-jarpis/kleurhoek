import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { addMessage, deleteConversation, setStatus } from "../actions";
import { CHANNEL_LABEL, STATUS_LABEL, TOPIC_LABEL, when } from "../labels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Gesprek" };

/**
 * Eén gesprek. Webberichten beantwoord je vanuit je eigen mail (knop opent je mailprogramma); leg daarna
 * vast wat je antwoordde, zodat collega's het zien. Via WhatsApp gaat een antwoord straks direct naar buiten.
 */
export default async function ConversationPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const [{ id }, q] = await Promise.all([params, searchParams]);
  let c, me;
  try { [c, me] = await Promise.all([adminApi.conversation(id), adminApi.me()]); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const canManage = me.permissions.includes("contact.manage");
  const first = c.messages.find((m) => m.direction === "in");
  const quote = first ? first.body.split("\n").map((l) => `> ${l}`).join("\n") : "";
  const mailto = c.email ? `mailto:${c.email}?subject=${encodeURIComponent("Je bericht aan Kleurhoek")}&body=${encodeURIComponent(`Hoi${c.name ? ` ${c.name}` : ""},\n\n\n\nGroet,\nKleurhoek\n\n${quote}`)}` : null;
  return (
    <>
      <div className="row-between">
        <div>
          <p className="lead"><Link href="/contact">← Inbox</Link></p>
          <h1>{c.name ?? c.email ?? c.phone ?? "Onbekend"}</h1>
          <p className="lead">{TOPIC_LABEL[c.topic]} · {CHANNEL_LABEL[c.channel]} · {c.org} · {c.market} · ontvangen {when(c.createdAt)}</p>
        </div>
        <span className={`pill ${c.status === "new" || c.status === "open" ? "on" : "off"}`}>{STATUS_LABEL[c.status]}</span>
      </div>
      {q.melding && <p className="note" role="status">{q.melding}</p>}
      {q.fout && <div className="err" role="alert"><p>{q.fout}</p></div>}

      <section className="panel stack">
        <h2>Afzender</h2>
        <p>{c.email && <><a href={`mailto:${c.email}`}>{c.email}</a><br /></>}{c.phone && <>{c.phone}<br /></>}<span className="lead">Gebruik deze gegevens alleen om te antwoorden.</span></p>
      </section>

      <ol className="ui-thread" aria-label="Berichten">
        {c.messages.map((m) => (
          <li key={m.id} data-direction={m.direction}>
            <header><b>{m.direction === "in" ? (c.name ?? "Afzender") : m.direction === "out" ? "Ons antwoord" : "Interne notitie"}</b><span>{m.author && m.direction !== "in" ? `${m.author} · ` : ""}{when(m.createdAt)}</span></header>
            {m.body}
          </li>
        ))}
      </ol>

      {canManage && (
        <>
          <section className="panel stack">
            <div className="row-between"><h2>Antwoorden</h2>{mailto && <a className="button" href={mailto}>Antwoord in je mail</a>}</div>
            <form action={addMessage} className="stack">
              <input type="hidden" name="id" value={c.id} />
              <label className="field"><span>Wat heb je geantwoord, of een notitie voor collega&apos;s</span><textarea name="body" rows={4} maxLength={8000} required /></label>
              <div className="checks">
                <button type="submit" name="direction" value="out">Vastleggen als antwoord</button>
                <button type="submit" name="direction" value="note" className="ghost">Opslaan als notitie</button>
              </div>
            </form>
          </section>
          <section className="panel stack">
            <h2>Status</h2>
            <form action={setStatus} className="checks">
              <input type="hidden" name="id" value={c.id} />
              {(["open", "answered", "closed", "new"] as const).filter((s) => s !== c.status).map((s) => (
                <button key={s} type="submit" name="status" value={s} className="ghost">Zet op {STATUS_LABEL[s].toLowerCase()}</button>
              ))}
            </form>
            <form action={deleteConversation} className="checks">
              <input type="hidden" name="id" value={c.id} />
              <label className="check"><input type="checkbox" name="confirm" value="ja" required /> Gesprek en gegevens nu verwijderen (bijvoorbeeld op verzoek)</label>
              <button type="submit" className="danger">Verwijderen</button>
            </form>
          </section>
        </>
      )}
    </>
  );
}
