"use client";
import { useEffect, useState } from "react";
import { logout } from "@/lib/account";
import type { Messages } from "@/i18n/nl";

/** Alleen teksten: functies kunnen niet van server- naar clientcomponent. */
export type AccountTexts = Pick<Messages, "login" | "logout" | "loading" | "accountError" | "name" | "email" | "memberSince" | "accountPrivacy" | "deleteAccount" | "deleteSure" | "mlAccount" | "mlAccountHint" | "mlTopicNames" | "mlSave" | "mlSaved" | "mlError">;

type Me = { displayName: string | null; email: string | null; createdAt: string };

/** Accountgegevens en verwijderen. Alles via de eigen /auth-routes; tokens komen nooit in de browser. */
export function AccountPanel({ market, t }: { market: string; t: AccountTexts }) {
  const [me, setMe] = useState<Me | null | "anon" | "error">(null);
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch("/auth/account").then(async (r) => {
      if (r.status === 401 || r.status === 404) return setMe("anon");
      setMe(r.ok ? ((await r.json()) as Me) : "error");
    }).catch(() => setMe("error"));
  }, []);

  if (me === null) return <p className="muted">{t.loading}</p>;
  if (me === "error") return <p className="muted">{t.accountError}</p>;
  if (me === "anon") return <p><a className="btn primary" href={`/auth/login?returnTo=${encodeURIComponent(`/${market}/account`)}`}>{t.login}</a></p>;

  async function remove() {
    if (!confirm) return setConfirm(true);
    setBusy(true);
    const res = await fetch("/auth/account", { method: "DELETE" });
    if (res.ok) await logout(); else { setBusy(false); setMe("error"); }
  }

  const since = new Intl.DateTimeFormat(marketLanguageOf(market), { dateStyle: "long" }).format(new Date(me.createdAt));
  return (
    <section className="panel">
      <dl className="facts">
        <dt>{t.name}</dt><dd>{me.displayName ?? "—"}</dd>
        <dt>{t.email}</dt><dd>{me.email ?? "—"}</dd>
        <dt>{t.memberSince}</dt><dd>{since}</dd>
      </dl>
      <MailTopics market={market} t={t} />
      <p className="muted">{t.accountPrivacy}</p>
      <div className="row">
        <button type="button" className="btn" onClick={() => void logout()}>{t.logout}</button>
        <button type="button" className="btn danger" disabled={busy} onClick={() => void remove()}>{confirm ? t.deleteSure : t.deleteAccount}</button>
      </div>
    </section>
  );
}

/** Mail vanuit het account (ADR 0037): onderwerpen aan- en uitvinken. */
function MailTopics({ market, t }: { market: string; t: AccountTexts }) {
  const [state, setState] = useState<{ topics: string[]; all: string[] } | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  useEffect(() => {
    fetch("/auth/mail").then(async (r) => { if (r.ok) { const d = (await r.json()) as { topics: string[]; topicsAll: string[] }; setState({ topics: d.topics, all: d.topicsAll }); } }).catch(() => undefined);
  }, []);
  if (!state) return null;
  const toggle = (k: string) => setState((s) => s && { ...s, topics: s.topics.includes(k) ? s.topics.filter((x) => x !== k) : [...s.topics, k] });
  async function save() {
    const r = await fetch("/auth/mail", { method: "PUT", headers: { "content-type": "application/json" }, body: JSON.stringify({ topics: state!.topics, market }) }).catch(() => null);
    setStatus(r?.ok ? t.mlSaved : t.mlError);
  }
  return (
    <fieldset className="ui-subscribe-topics">
      <legend>{t.mlAccount}</legend>
      <p className="ui-hint">{t.mlAccountHint}</p>
      {state.all.map((k) => <label key={k} className="chk"><input type="checkbox" checked={state.topics.includes(k)} onChange={() => toggle(k)} /> {t.mlTopicNames[k] ?? k}</label>)}
      <div className="row"><button type="button" className="btn" onClick={() => void save()}>{t.mlSave}</button><span role="status" className="muted">{status}</span></div>
    </fieldset>
  );
}

function marketLanguageOf(market: string) { return market.split("-")[0] ?? "nl"; }
