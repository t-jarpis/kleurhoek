"use client";
import { useEffect, useState } from "react";
import { messages } from "@/i18n/nl";

type Prefs = { email: string; topics: string[]; topicsAll: string[] };

/** Voorkeuren en afmelden met de link uit een mail (design system: MailPreferences, ADR 0037). */
export function MailPreferences({ token, language, unsubscribe }: { token: string; language: string; unsubscribe: boolean }) {
  const t = messages(language);
  const [prefs, setPrefs] = useState<Prefs | "invalid" | "removed" | null>(null);
  const [topics, setTopics] = useState<string[]>([]);
  const [sure, setSure] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`/mail/voorkeuren?t=${encodeURIComponent(token)}`).then(async (r) => {
      if (!r.ok) return setPrefs("invalid");
      const p = (await r.json()) as Prefs;
      setPrefs(p); setTopics(p.topics);
    }).catch(() => setPrefs("invalid"));
  }, [token]);

  if (prefs === null) return <p className="muted">{t.loading}</p>;
  if (prefs === "invalid") return <div className="ui-callout" data-tone="warning" role="status"><div>{t.mlLinkInvalid}</div></div>;
  if (prefs === "removed") return <div className="ui-callout" data-tone="success" role="status"><div><strong>{t.mlUnsubscribed}</strong>{t.mlUnsubscribedText}</div></div>;

  async function save() {
    setBusy(true);
    const r = await fetch("/mail/voorkeuren", { method: "PUT", headers: { "content-type": "application/json" }, body: JSON.stringify({ t: token, topics }) }).catch(() => null);
    setBusy(false);
    if (r?.ok && ((await r.json()) as { status: string }).status === "removed") return setPrefs("removed");
    setStatus(r?.ok ? t.mlSaved : t.mlError);
  }
  async function remove() {
    if (!sure) return setSure(true);
    setBusy(true);
    const r = await fetch("/mail/afmelden", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ t: token }) }).catch(() => null);
    setBusy(false);
    if (r?.ok) setPrefs("removed"); else setStatus(t.mlError);
  }

  return (
    <section className="panel ui-subscribe">
      <p className="facts-line">{t.mlPrefsFor} {prefs.email}</p>
      <fieldset className="ui-subscribe-topics">
        <legend>{t.mlTopics}</legend>
        {prefs.topicsAll.map((k) => (
          <label key={k} className="chk"><input type="checkbox" checked={topics.includes(k)} onChange={() => setTopics((x) => (x.includes(k) ? x.filter((y) => y !== k) : [...x, k]))} /> {t.mlTopicNames[k] ?? k}</label>
        ))}
      </fieldset>
      <div className="row">
        <button type="button" className="ui-btn" data-variant="primary" disabled={busy} onClick={() => void save()}>{t.mlSave}</button>
        <button type="button" className="ui-btn" data-variant={unsubscribe || sure ? "danger" : "quiet"} disabled={busy} onClick={() => void remove()} autoFocus={unsubscribe}>{sure ? t.mlUnsubscribeSure : t.mlUnsubscribe}</button>
      </div>
      <p role="status" className="ui-hint">{status}</p>
    </section>
  );
}
