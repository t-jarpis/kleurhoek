import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { deleteTemplate } from "../actions";
import { KIND_LABEL, MailNav } from "../nav";

export const metadata = { title: "Templates · Mail" };
export const dynamic = "force-dynamic";

/** Templates (ADR 0037): blokken met tekst per taal. Vaste templates (bevestigen, welkom) kunnen niet weg. */
export default async function Templates({ searchParams }: { searchParams: Promise<{ melding?: string }> }) {
  const { melding } = await searchParams;
  let data;
  try {
    const [list, me] = await Promise.all([adminApi.mailTemplates(), adminApi.me()]);
    data = { ...list, canManage: me.permissions.includes("mail.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { templates, options, canManage } = data;
  /** Talen van de site waarin het onderwerp of een tekst nog ontbreekt. */
  const missing = (t: (typeof templates)[number]) => options.languages.filter((l) => !t.subject[l] || t.blocks.some((b) => ("text" in b && !b.text[l]) || ("label" in b && !b.label[l])));
  return (
    <>
      <div><h1>Templates</h1><p className="lead">Waaruit een mail bestaat: kop, tekst, knoppen en platen, per taal. Ontbreekt een taal, dan krijgt die abonnee de Nederlandse tekst.</p></div>
      <div className="toolbar"><MailNav active="templates" />{canManage && <Link className="ui-btn" data-variant="primary" href="/mail/templates/nieuw">Nieuwe template</Link>}</div>
      {melding && <p className="note" role="status">{melding}</p>}
      <section className="panel">
        <table>
          <thead><tr><th>Naam</th><th>Soort</th><th>Onderwerp</th><th>Talen</th><th>Gewijzigd</th><th><span className="visually-hidden">Acties</span></th></tr></thead>
          <tbody>{templates.map((t) => {
            const gaps = missing(t);
            return (
              <tr key={t.slug}>
                <td><Link href={`/mail/templates/${t.slug}`}>{t.name}</Link><br /><code>{t.slug}</code></td>
                <td><span className="ui-badge" {...(t.kind === "system" ? { "data-tone": "accent" } : {})}>{KIND_LABEL[t.kind]}</span></td>
                <td>{t.subject.nl}</td>
                <td>{gaps.length ? <span className="ui-badge" data-tone="warning">Onvolledig: {gaps.join(", ")}</span> : <span className="ui-badge" data-tone="success">Compleet</span>}</td>
                <td>{new Date(t.updatedAt).toLocaleDateString("nl-NL", { dateStyle: "medium" })}<br /><small>{t.updatedBy}</small></td>
                <td>{canManage && t.kind !== "system" && <form action={deleteTemplate}><input type="hidden" name="slug" value={t.slug} /><button type="submit" className="ghost">Verwijderen<span className="visually-hidden"> {t.name}</span></button></form>}</td>
              </tr>
            );
          })}</tbody>
        </table>
      </section>
    </>
  );
}
