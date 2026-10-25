"use client";
import { useActionState, useEffect, useState } from "react";
import type { SubscribeState } from "@/app/[org]/[market]/mail/actions";
import { messages } from "@/i18n/nl";

const TOPICS = ["nieuwe-platen", "feestdagen", "nieuwsbrief"] as const;

/**
 * Aanmelden voor mail (design system: SubscribeForm, ADR 0037). Ouderzone; verklaring 16+ (ADR 0002); geen captcha,
 * wel een verborgen veld en een minimale invultijd. Na versturen: "kijk in je mail" (double opt-in).
 */
export function SubscribeForm({ action, language }: { action: (s: SubscribeState, f: FormData) => Promise<SubscribeState>; language: string }) {
  const t = messages(language);
  const [state, submit, pending] = useActionState(action, { status: "idle" });
  const [started, setStarted] = useState(0);
  useEffect(() => { setStarted(Date.now()); }, []);

  return (
    <section className="ui-subscribe panel no-print" data-mode="ouder" aria-labelledby="kh-sub-title">
      <h2 id="kh-sub-title">{t.mlTitle}</h2>
      {state.status === "sent" ? (
        <div className="ui-callout" data-tone="success" role="status"><div><strong>{t.mlCheckTitle}</strong>{t.mlCheckText}</div></div>
      ) : (
        <form action={submit} className="ui-subscribe-form">
          <p className="ui-hint">{t.mlIntro}</p>
          {(state.status === "invalid" || state.status === "error" || state.status === "busy") && (
            <div className="ui-callout" data-tone="danger" role="alert"><div>{state.status === "busy" ? t.mlBusy : t.mlError}</div></div>
          )}
          <div className="ui-field">
            <label htmlFor="kh-sub-email">{t.mlEmail}</label>
            <input id="kh-sub-email" name="email" type="email" className="ui-input" autoComplete="email" required maxLength={254} defaultValue={state.email} />
          </div>
          <fieldset className="ui-subscribe-topics">
            <legend>{t.mlTopics}</legend>
            {TOPICS.map((k) => <label key={k} className="chk"><input type="checkbox" name="topics" value={k} defaultChecked={k !== "nieuwsbrief"} /> {t.mlTopicNames[k]}</label>)}
          </fieldset>
          <label className="chk"><input type="checkbox" name="adult" required /> {t.mlAdult}</label>
          <div className="ui-trap" aria-hidden="true"><label htmlFor="kh-sub-website">Website</label><input id="kh-sub-website" name="website" tabIndex={-1} autoComplete="off" /></div>
          <input type="hidden" name="started" value={started || ""} />
          <div className="row"><button type="submit" className="ui-btn" data-variant="primary" disabled={pending}>{pending ? t.mlSending : t.mlSubmit}</button></div>
          <p className="ui-hint">{t.mlPrivacy}</p>
        </form>
      )}
    </section>
  );
}
