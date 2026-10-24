"use client";
import { useActionState, useEffect, useState } from "react";
import type { ContactState } from "@/app/[org]/[market]/contact/actions";

type T = {
  contactTopic: string; contactTopics: Record<string, string>; contactName: string; contactNameHint: string; contactEmail: string; contactEmailHint: string;
  contactMessage: string; contactSend: string; contactSending: string; contactPrivacy: string; contactThanks: string; contactThanksText: string;
  contactError: string; contactTooMany: string; contactClosed: string;
};

/** Contactformulier (ADR 0024): geen captcha, wel een verborgen veld en een minimale invultijd tegen spam. */
export function ContactForm({ action, t, initialTopic }: { action: (s: ContactState, f: FormData) => Promise<ContactState>; t: T; initialTopic: string }) {
  const [state, submit, pending] = useActionState(action, { status: "idle" });
  const [started, setStarted] = useState(0);
  useEffect(() => { setStarted(Date.now()); }, []);

  if (state.status === "sent") {
    return <div className="ui-callout" data-tone="success" role="status"><div><strong>{t.contactThanks}</strong>{t.contactThanksText}</div></div>;
  }
  const f = state.fields ?? {};
  const problem = state.status === "invalid" || state.status === "error" ? t.contactError : state.status === "busy" ? t.contactTooMany : state.status === "closed" ? t.contactClosed : null;
  return (
    <form action={submit} className="kh-contact" noValidate={false}>
      {problem && <div className="ui-callout" data-tone="danger" role="alert"><div>{problem}</div></div>}
      <div className="ui-field">
        <label htmlFor="c-topic">{t.contactTopic}</label>
        <select id="c-topic" name="topic" className="ui-select" defaultValue={f.topic ?? initialTopic} required>
          {Object.entries(t.contactTopics).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      <div className="kh-contact-row">
        <div className="ui-field">
          <label htmlFor="c-name">{t.contactName}</label>
          <input id="c-name" name="name" className="ui-input" autoComplete="name" maxLength={80} defaultValue={f.name} aria-describedby="c-name-hint" />
          <span className="ui-hint" id="c-name-hint">{t.contactNameHint}</span>
        </div>
        <div className="ui-field">
          <label htmlFor="c-email">{t.contactEmail}</label>
          <input id="c-email" name="email" type="email" className="ui-input" autoComplete="email" required maxLength={200} defaultValue={f.email} aria-describedby="c-email-hint" />
          <span className="ui-hint" id="c-email-hint">{t.contactEmailHint}</span>
        </div>
      </div>
      <div className="ui-field">
        <label htmlFor="c-message">{t.contactMessage}</label>
        <textarea id="c-message" name="message" className="ui-textarea" required minLength={10} maxLength={4000} rows={6} defaultValue={f.message} />
      </div>
      <div className="ui-trap" aria-hidden="true">
        <label htmlFor="c-website">Website</label>
        <input id="c-website" name="website" tabIndex={-1} autoComplete="off" />
      </div>
      <input type="hidden" name="started" value={started || ""} />
      <p className="ui-hint">{t.contactPrivacy}</p>
      <button type="submit" className="ui-btn" data-variant="primary" disabled={pending}>{pending ? t.contactSending : t.contactSend}</button>
    </form>
  );
}
