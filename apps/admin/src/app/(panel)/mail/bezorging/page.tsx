import Link from "next/link";
import { TimeChart } from "@/components/charts/TimeChart";
import { num } from "@/components/charts/format";
import { CopyButton } from "@/components/CopyButton";
import { adminApi, describe, type MailCounts, type MailHealth, type MailSuppressionLookup } from "@/lib/api";
import { suppressAddress, unsuppressAddress } from "../actions";
import { MailNav } from "../nav";

export const metadata = { title: "Bezorging · Mail" };
export const dynamic = "force-dynamic";

const PERIODS = [7, 30, 90] as const;
const pct = (v: number) => `${(v * 100).toLocaleString("nl-NL", { maximumFractionDigits: v < 0.01 ? 2 : 1 })} %`;
const TYPE_LABEL: Record<string, string> = {
  sent: "Verstuurd", delivered: "Afgeleverd", deferred: "Vertraagd", soft_bounce: "Soft bounce", hard_bounce: "Harde bounce", complaint: "Spamklacht", unsubscribe: "Afgemeld bij de relay",
};
const REASON_LABEL: Record<string, string> = { hard_bounce: "Harde bounce", soft_bounce: "Herhaalde soft bounces (90 dagen)", complaint: "Spamklacht", manual: "Handmatig" };
const PROVIDER_LABEL: Record<string, string> = { smtp: "SMTP", brevo: "Brevo", scaleway: "Scaleway TEM", generic: "Eigen formaat" };
const HEALTH: Record<MailHealth, { label: string; tone?: string }> = { goed: { label: "Goed", tone: "success" }, "let op": { label: "Let op", tone: "warning" }, slecht: { label: "Slecht", tone: "danger" }, "te weinig": { label: "Te weinig mail" } };
const sourceLabel = (s: string | null, template: string | null) => {
  if (!s) return "—";
  if (s.startsWith("wf:")) return `Workflow ${s.split(":")[1]}`;
  if (s.startsWith("campaign:")) return `Campagne (${template ?? "?"})`;
  if (s.startsWith("system:confirm")) return "Bevestigingsmail";
  return s;
};
const bounces = (c: MailCounts) => c.hard + c.soft;
const when = (iso: string) => new Date(iso).toLocaleString("nl-NL", { dateStyle: "medium", timeStyle: "short" });

function Health({ label, rate, health, part, total, limit }: { label: string; rate: number; health: MailHealth; part: number; total: number; limit: { warn: number; bad: number } }) {
  const h = HEALTH[health];
  return (
    <div className="ui-health">
      <span>{label}</span>
      <strong>{pct(rate)}</strong>
      <span className="ui-badge" {...(h.tone ? { "data-tone": h.tone } : {})}>{h.label}</span>
      <small>{num(part)} van {num(total)} mails · let op vanaf {pct(limit.warn)}, slecht vanaf {pct(limit.bad)}</small>
    </div>
  );
}

/**
 * Bezorging (ADR 0038): wat er met verstuurde mails gebeurde, uit SMTP-antwoorden en meldingen van de relay.
 * Alles in het eigen platform; de relay is alleen een doorgeefluik. Geen e-mailadressen in de lijsten.
 */
export default async function DeliverabilityPage({ searchParams }: { searchParams: Promise<{ dagen?: string; email?: string; melding?: string }> }) {
  const { dagen, email, melding } = await searchParams;
  const days = PERIODS.find((p) => String(p) === dagen) ?? 30;
  let data;
  try {
    const [report, me] = await Promise.all([adminApi.mailDeliverability(days), adminApi.me()]);
    const canManage = me.permissions.includes("mail.manage");
    const [webhooks, lookup] = await Promise.all([
      canManage ? adminApi.mailWebhooks() : Promise.resolve(null),
      canManage && email ? adminApi.mailSuppression(email).catch(() => null) : Promise.resolve(undefined as MailSuppressionLookup | null | undefined),
    ]);
    data = { report, canManage, webhooks, lookup };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { report: r, canManage, webhooks, lookup } = data;
  const t = r.totals;
  // Elke dag in de periode, ook zonder mail.
  const dates = Array.from({ length: days }, (_, i) => new Date(Date.now() - (days - 1 - i) * 86_400_000).toISOString().slice(0, 10));
  const byDay = new Map(r.daily.map((d) => [d.day, d]));
  const series = (f: (c: MailCounts) => number) => dates.map((d) => { const c = byDay.get(d); return c ? f(c) : 0; });
  const blocked = Object.values(r.suppressed).reduce((a, b) => a + b, 0);
  const noFeedback = Object.keys(r.providers).length === 0;

  return (
    <>
      <div>
        <h1>Bezorging</h1>
        <p className="lead">Wat er met de mails gebeurde: afgeleverd, gebounced of als spam gemeld. Uit de antwoorden van de mailserver en de meldingen van de relay, allemaal hier. Bij een harde bounce of spamklacht verdwijnt de abonnee en gaat het adres op de blokkeerlijst.</p>
      </div>
      <div className="toolbar"><MailNav active="bezorging" />
        <nav className="tabs" aria-label="Periode">{PERIODS.map((p) => <Link key={p} href={`/mail/bezorging?dagen=${p}`} aria-current={p === days ? "page" : undefined}>{p} dagen</Link>)}</nav>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}
      {noFeedback && (
        <div className="ui-callout" data-tone="warning"><p><strong>Nog geen meldingen van de relay.</strong> Zonder webhook zie je alleen wat de mailserver direct weigert, niet wat later bounced of als spam gemeld wordt. Stel hieronder de webhook in bij je mailrelay.</p></div>
      )}
      <div className="ui-stats">
        <div className="ui-stat"><span>Verstuurd</span><strong>{num(t.sent)}</strong><p className="ui-stat-note">laatste {days} dagen</p></div>
        <div className="ui-stat"><span>Afgeleverd</span><strong>{r.rates.delivered === null ? "—" : pct(r.rates.delivered)}</strong><p className="ui-stat-note">{num(t.delivered)} gemeld{noFeedback ? " (geen meldingen)" : ""}</p></div>
        <Health label="Bounces" rate={r.rates.bounce} health={r.health.bounce} part={bounces(t)} total={t.sent} limit={r.limits.bounce} />
        <Health label="Spamklachten" rate={r.rates.complaint} health={r.health.complaint} part={t.complaints} total={t.sent} limit={r.limits.complaint} />
        <div className="ui-stat"><span>Geblokkeerd</span><strong>{num(blocked)}</strong><p className="ui-stat-note">{Object.entries(r.suppressed).map(([k, v]) => `${v} ${REASON_LABEL[k]?.toLowerCase() ?? k}`).join(", ") || "geen adressen"}</p></div>
      </div>

      <section className="panel stack">
        <h2>Per dag</h2>
        <TimeChart title="Verstuurd en afgeleverd" dates={dates} bucket="day" series={[
          { key: "sent", label: "Verstuurd", color: "var(--chart-1)", values: series((c) => c.sent) },
          { key: "delivered", label: "Afgeleverd", color: "var(--chart-4)", values: series((c) => c.delivered) },
        ]} />
        <TimeChart title="Bounces en klachten" kind="bar" dates={dates} bucket="day" series={[
          { key: "bounces", label: "Bounces", color: "var(--chart-2)", values: series(bounces) },
          { key: "complaints", label: "Spamklachten", color: "var(--chart-3)", values: series((c) => c.complaints) },
        ]} />
      </section>

      <section className="panel">
        <h2>Per mailprovider van de ontvanger</h2>
        <p className="lead">Weigert één provider ineens veel (bijvoorbeeld Outlook), dan zie je dat hier eerst.</p>
        {r.byDomain.length === 0 ? <p className="lead">Nog geen mail in deze periode.</p> : (
          <table>
            <thead><tr><th>Domein</th><th className="num">Verstuurd</th><th className="num">Afgeleverd</th><th className="num">Vertraagd</th><th className="num">Bounces</th><th className="num">Klachten</th></tr></thead>
            <tbody>{r.byDomain.map((d) => <tr key={d.domain}><td>{d.domain}</td><td className="num">{num(d.sent)}</td><td className="num">{num(d.delivered)}</td><td className="num">{num(d.deferred)}</td><td className="num">{num(bounces(d))}</td><td className="num">{num(d.complaints)}</td></tr>)}</tbody>
          </table>
        )}
      </section>

      <section className="panel">
        <h2>Per mail</h2>
        {r.bySource.length === 0 ? <p className="lead">Nog geen mail in deze periode.</p> : (
          <table>
            <thead><tr><th>Bron</th><th className="num">Verstuurd</th><th className="num">Afgeleverd</th><th className="num">Bounces</th><th className="num">Klachten</th><th className="num">Afgemeld</th></tr></thead>
            <tbody>{r.bySource.map((s) => <tr key={s.source ?? ""}><td>{sourceLabel(s.source, s.template)}</td><td className="num">{num(s.sent)}</td><td className="num">{num(s.delivered)}</td><td className="num">{num(bounces(s))}</td><td className="num">{num(s.complaints)}</td><td className="num">{num(s.unsubscribes)}</td></tr>)}</tbody>
          </table>
        )}
      </section>

      <section className="panel">
        <h2>Laatste meldingen</h2>
        {r.recent.length === 0 ? <p className="lead">Geen bounces, klachten of vertragingen in deze periode.</p> : (
          <table>
            <thead><tr><th>Wanneer</th><th>Wat</th><th>Domein</th><th>Mail</th><th>Reden</th><th>Via</th></tr></thead>
            <tbody>{r.recent.map((e, i) => <tr key={i}><td>{when(e.at)}</td><td>{TYPE_LABEL[e.type] ?? e.type}</td><td>{e.domain}</td><td>{sourceLabel(e.source, e.template ?? null)}</td><td>{e.reason ?? "—"}</td><td>{PROVIDER_LABEL[e.provider] ?? e.provider}</td></tr>)}</tbody>
          </table>
        )}
      </section>

      {canManage && (
        <section className="panel stack">
          <h2>Adres opzoeken of blokkeren</h2>
          <p className="lead">Op exact adres. De blokkeerlijst bevat geen adressen, alleen een versleutelde vingerafdruk; opzoeken kan dus alleen als je het adres al weet.</p>
          <form className="grid-form" method="get">
            <input type="hidden" name="dagen" value={days} />
            <label className="field"><span>E-mailadres</span><input name="email" type="email" defaultValue={email ?? ""} autoComplete="off" required /></label>
            <div><button type="submit">Opzoeken</button></div>
          </form>
          {email && lookup === null && <p className="lead">Dat lukte niet. Is het een geldig adres?</p>}
          {email && lookup && (
            <div className="stack">
              {lookup.suppression ? (
                <dl className="facts">
                  <dt>Stand</dt><dd><span className="ui-badge" data-tone="danger">Geblokkeerd</span> {REASON_LABEL[lookup.suppression.reason] ?? lookup.suppression.reason}</dd>
                  <dt>Sinds</dt><dd>{when(lookup.suppression.since)}{lookup.suppression.expiresAt ? `, tot ${when(lookup.suppression.expiresAt)}` : ", blijvend"}</dd>
                  <dt>Door</dt><dd>{PROVIDER_LABEL[lookup.suppression.by] ?? lookup.suppression.by}</dd>
                  {lookup.suppression.detail && <><dt>Reden</dt><dd>{lookup.suppression.detail}</dd></>}
                </dl>
              ) : <p className="lead"><span className="ui-badge" data-tone="success">Niet geblokkeerd</span></p>}
              {lookup.events.length > 0 && (
                <table>
                  <thead><tr><th>Wanneer</th><th>Wat</th><th>Mail</th><th>Reden</th></tr></thead>
                  <tbody>{lookup.events.map((e, i) => <tr key={i}><td>{when(e.at)}</td><td>{TYPE_LABEL[e.type] ?? e.type}</td><td>{sourceLabel(e.source, null)}</td><td>{e.reason ?? "—"}</td></tr>)}</tbody>
                </table>
              )}
              {lookup.suppression ? (
                <form action={unsuppressAddress}><input type="hidden" name="email" value={email} /><button type="submit">Vrijgeven</button></form>
              ) : (
                <form action={suppressAddress} className="grid-form">
                  <input type="hidden" name="email" value={email} />
                  <label className="field"><span>Reden (optioneel)</span><input name="detail" maxLength={200} placeholder="Bijvoorbeeld: gevraagd per mail" /></label>
                  <div><button type="submit" className="danger">Blokkeren</button></div>
                </form>
              )}
            </div>
          )}
        </section>
      )}

      {canManage && webhooks && (
        <section className="panel stack">
          <h2>Meldingen van de relay instellen</h2>
          <p className="lead">Zet bij je mailrelay een webhook op het adres hieronder, voor de gebeurtenissen afgeleverd, vertraagd, soft en hard bounce, spam en afgemeld. Het adres bevat een geheime sleutel: deel het niet. Elke mail heeft onze eigen Message-ID en de header X-Mail-Ref, zodat meldingen van elke dienst bij de juiste mail terechtkomen.</p>
          <table>
            <thead><tr><th>Dienst</th><th>Webhookadres</th><th>Laatste melding</th></tr></thead>
            <tbody>{Object.entries(webhooks).map(([p, url]) => (
              <tr key={p}>
                <td>{PROVIDER_LABEL[p] ?? p}</td>
                <td><span className="ui-copy"><code id={`hook-${p}`} style={{ overflowWrap: "anywhere" }}>{url}</code><CopyButton value={url} label="Kopieer adres" targetId={`hook-${p}`} /></span></td>
                <td>{r.providers[p] ? `${when(r.providers[p]!.last)} (${num(r.providers[p]!.events)} totaal)` : "Nog nooit"}</td>
              </tr>
            ))}</tbody>
          </table>
          <small>Brevo: Transactional › Settings › Webhooks. Scaleway TEM: een webhook naar een Topics and Events-onderwerp met een HTTPS-abonnement op dit adres (bevestigen gaat vanzelf). Eigen mailserver of script: POST <code>{`{"events":[{"type":"hard_bounce","email":"…","messageId":"…","reason":"…"}]}`}</code> naar het adres van &quot;Eigen formaat&quot;.</small>
        </section>
      )}
    </>
  );
}
