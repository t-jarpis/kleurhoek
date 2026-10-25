import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { cancelCampaign, scheduleCampaign } from "../actions";
import { MailNav, TOPIC_LABEL } from "../nav";
import { NewCampaign } from "./NewCampaign";

export const metadata = { title: "Campagnes · Mail" };
export const dynamic = "force-dynamic";

const STATUS: Record<string, { label: string; tone?: string }> = {
  draft: { label: "Concept" }, scheduled: { label: "Gepland", tone: "accent" }, sending: { label: "Bezig", tone: "accent" },
  sent: { label: "Verstuurd", tone: "success" }, cancelled: { label: "Geannuleerd", tone: "warning" },
};
const when = (d: string | null) => (d ? new Date(d).toLocaleString("nl-NL", { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Amsterdam" }) : "—");

/** Campagnes (ADR 0037): een nieuwsbrief of losse mail aan abonnees van gekozen onderwerpen, nu of later. */
export default async function Campaigns({ searchParams }: { searchParams: Promise<{ melding?: string }> }) {
  const { melding } = await searchParams;
  let data;
  try {
    const [list, overview, me] = await Promise.all([adminApi.mailCampaigns(), adminApi.mailOverview(), adminApi.me()]);
    data = { ...list, overview, canManage: me.permissions.includes("mail.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { campaigns, options, overview, canManage } = data;
  const templates = options.templates.filter((t) => t.kind !== "system");
  const name = new Map(options.templates.map((t) => [t.slug, t.name]));
  return (
    <>
      <div><h1>Campagnes</h1><p className="lead">Een mail aan iedereen die een onderwerp koos, nu of op een tijdstip. Maak de inhoud bij <Link href="/mail/templates">Templates</Link>; stuur jezelf daar eerst een testmail.</p></div>
      <div className="toolbar"><MailNav active="campagnes" /></div>
      {melding && <p className="note" role="status">{melding}</p>}
      {!overview.sending.bulk && <div className="ui-callout" data-tone="warning"><p><strong>Versturen staat uit.</strong> Een campagne gaat in de wachtrij en vervalt na 3 dagen als er dan nog geen SMTP-dienst is ingesteld.</p></div>}
      {canManage && <section className="panel stack"><h2>Nieuwe campagne</h2><NewCampaign templates={templates} topics={options.topics} markets={options.markets} counts={overview.subscribers.byTopic} /></section>}
      <section className="panel">
        <h2>Alle campagnes</h2>
        {campaigns.length === 0 ? <p className="lead">Nog geen campagnes.</p> : (
          <table>
            <thead><tr><th>Naam</th><th>Template</th><th>Aan</th><th>Stand</th><th>Wanneer</th><th className="num">Ontvangers</th><th><span className="visually-hidden">Acties</span></th></tr></thead>
            <tbody>{campaigns.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td><Link href={`/mail/templates/${c.template}`}>{name.get(c.template) ?? c.template}</Link></td>
                <td>{c.audience.topics.map((t) => TOPIC_LABEL[t] ?? t).join(", ")}{c.audience.markets ? ` · ${c.audience.markets.join(", ")}` : ""}</td>
                <td><span className="ui-badge" {...(STATUS[c.status]?.tone ? { "data-tone": STATUS[c.status]!.tone } : {})}>{STATUS[c.status]?.label ?? c.status}</span></td>
                <td>{c.status === "scheduled" ? when(c.scheduledAt) : when(c.sentAt)}</td>
                <td className="num">{c.recipients || "—"}{c.deliveries.sent !== undefined && <small><br />{c.deliveries.sent} weg{c.deliveries.queued ? `, ${c.deliveries.queued} wachten` : ""}{c.deliveries.failed ? `, ${c.deliveries.failed} mislukt` : ""}</small>}</td>
                <td>{canManage && (c.status === "draft" || c.status === "scheduled") && (
                  <div className="stack">
                    <form action={scheduleCampaign} className="row"><input type="hidden" name="id" value={c.id} /><label className="check"><input type="checkbox" required /> Testmail bekeken</label><button type="submit">Nu versturen</button></form>
                    <form action={scheduleCampaign} className="row"><input type="hidden" name="id" value={c.id} /><label className="field"><span className="visually-hidden">Tijdstip</span><input type="datetime-local" name="at" required /></label><button type="submit">Plannen</button></form>
                    <form action={cancelCampaign}><input type="hidden" name="id" value={c.id} /><button type="submit" className="ghost">Annuleren</button></form>
                  </div>
                )}{canManage && c.status === "sent" && (c.deliveries.queued ?? 0) > 0 && <form action={cancelCampaign}><input type="hidden" name="id" value={c.id} /><button type="submit" className="ghost">Rest niet meer sturen</button></form>}</td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </section>
    </>
  );
}
