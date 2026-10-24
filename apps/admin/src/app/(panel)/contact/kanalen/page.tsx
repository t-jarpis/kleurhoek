import { adminApi, describe } from "@/lib/api";
import { toggleChannel } from "../actions";
import { CHANNEL_LABEL, ContactNav } from "../labels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Contactkanalen" };

const ABOUT = {
  web: "Het contactformulier op de website (/contact). Uitzetten verbergt het formulier niet, maar weigert nieuwe berichten.",
  whatsapp: "Berichten via WhatsApp komen in dezelfde inbox, en je antwoordt vanuit het admin panel.",
} as const;

/** Kanalen (ADR 0024): web is er altijd; WhatsApp koppelen we als volgende stap. */
export default async function Channels({ searchParams }: { searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const q = await searchParams;
  let channels, me;
  try { [channels, me] = await Promise.all([adminApi.contactChannels(), adminApi.me()]); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const canManage = me.permissions.includes("contact.manage");
  return (
    <>
      <div className="row-between">
        <div><h1>Kanalen</h1><p className="lead">Waarlangs bezoekers je kunnen bereiken. Alle berichten komen in één inbox.</p></div>
        <ContactNav active="kanalen" />
      </div>
      {q.melding && <p className="note" role="status">{q.melding}</p>}
      {q.fout && <div className="err" role="alert"><p>{q.fout}</p></div>}
      {channels.map((c) => (
        <section key={c.slug} className="panel stack">
          <div className="row-between">
            <h2>{CHANNEL_LABEL[c.slug]}</h2>
            <span className={`pill ${c.enabled ? "on" : "off"}`}>{c.enabled ? "Aan" : c.connected ? "Uit" : "Nog niet gekoppeld"}</span>
          </div>
          <p className="lead">{ABOUT[c.slug]}</p>
          {c.slug === "whatsapp" && !c.connected && (
            <div className="note">
              <p><b>Zo koppelen we WhatsApp</b> (volgende stap, ADR 0024):</p>
              <ol>
                <li>Een Meta Business-account en een WhatsApp Business-nummer (WhatsApp Cloud API).</li>
                <li>Het toegangstoken en app-geheim gaan in de secret manager van Scaleway, nooit in het admin panel.</li>
                <li>De website krijgt een webhook-adres waar Meta nieuwe berichten naartoe stuurt; die komen hier in de inbox.</li>
                <li>Daarna zet je het kanaal hier aan en antwoord je direct vanuit een gesprek.</li>
              </ol>
            </div>
          )}
          {canManage && c.connected && (
            <form action={toggleChannel} className="inline">
              <input type="hidden" name="slug" value={c.slug} />
              <input type="hidden" name="enabled" value={String(!c.enabled)} />
              <button type="submit" className="ghost">{c.enabled ? "Uitzetten" : "Aanzetten"}</button>
              <span className="lead">Laatst gewijzigd door {c.updatedBy}</span>
            </form>
          )}
        </section>
      ))}
    </>
  );
}
