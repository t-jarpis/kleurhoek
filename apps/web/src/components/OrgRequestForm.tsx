"use client";
import { useActionState, useEffect, useState } from "react";
import type { ContactState, PowChallenge } from "@/app/[org]/[market]/contact/actions";
import { usePow } from "./usePow";

export type OrgRequestTexts = {
  orgName: string; orgKind: string; orgKinds: Record<string, string>; orgCode: string; orgCodeHint: string; orgCodeExample: string;
  orgChildren: string; orgChildrenHint: string; orgSite: string; contactName: string; contactEmail: string; contactEmailHint: string;
  orgMessage: string; orgMessagePlaceholder: string; orgSend: string; contactSending: string; contactPrivacy: string;
  orgThanks: string; orgThanksText: string; contactError: string; contactTooMany: string; contactClosed: string; optionalField: string;
};

const slug = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 32);

/** Aanvraagformulier voor een eigen omgeving (ADR 0028). Zelfde spambescherming als het contactformulier. */
export function OrgRequestForm({ action, challenge, t }: { action: (s: ContactState, f: FormData) => Promise<ContactState>; challenge: () => Promise<PowChallenge | null>; t: OrgRequestTexts }) {
  const [state, submit, pending] = useActionState(action, { status: "idle" });
  const pow = usePow(challenge, state.status);
  const [started, setStarted] = useState(0);
  const f = state.fields ?? {};
  const [name, setName] = useState(f.organization ?? "");
  const [code, setCode] = useState(f.code ?? "");
  const [touched, setTouched] = useState(Boolean(f.code));
  useEffect(() => { setStarted(Date.now()); }, []);

  if (state.status === "sent") {
    return <div className="ui-callout" data-tone="success" role="status"><div><strong>{t.orgThanks}</strong>{t.orgThanksText}</div></div>;
  }
  const shown = touched ? code : slug(name);
  const problem = state.status === "invalid" || state.status === "error" ? t.contactError : state.status === "busy" ? t.contactTooMany : state.status === "closed" ? t.contactClosed : null;
  return (
    <form action={submit} className="kh-contact">
      {problem && <div className="ui-callout" data-tone="danger" role="alert"><div>{problem}</div></div>}
      <div className="kh-contact-row">
        <div className="ui-field">
          <label htmlFor="o-name">{t.orgName}</label>
          <input id="o-name" name="organization" className="ui-input" required minLength={2} maxLength={120} autoComplete="organization" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="ui-field">
          <label htmlFor="o-kind">{t.orgKind}</label>
          <select id="o-kind" name="kind" className="ui-select" defaultValue={f.kind ?? "school"} required>
            {Object.entries(t.orgKinds).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
      </div>
      <div className="ui-field">
        <label htmlFor="o-code">{t.orgCode} <span className="ui-hint">({t.optionalField})</span></label>
        <input id="o-code" name="code" className="ui-input" maxLength={32} spellCheck={false} autoCapitalize="none" value={shown} aria-describedby="o-code-hint"
          onChange={(e) => { setTouched(true); setCode(e.target.value.toLowerCase()); }} />
        <span className="ui-hint" id="o-code-hint">{t.orgCodeHint.replace("{host}", `${shown || t.orgCodeExample}.kleurhoek.nl`)}</span>
      </div>
      <div className="kh-contact-row">
        <div className="ui-field">
          <label htmlFor="o-children">{t.orgChildren} <span className="ui-hint">({t.optionalField})</span></label>
          <input id="o-children" name="children" className="ui-input" maxLength={40} defaultValue={f.children} aria-describedby="o-children-hint" />
          <span className="ui-hint" id="o-children-hint">{t.orgChildrenHint}</span>
        </div>
        <div className="ui-field">
          <label htmlFor="o-site">{t.orgSite} <span className="ui-hint">({t.optionalField})</span></label>
          <input id="o-site" name="orgSite" className="ui-input" maxLength={200} inputMode="url" autoComplete="url" defaultValue={f.orgSite} />
        </div>
      </div>
      <div className="kh-contact-row">
        <div className="ui-field">
          <label htmlFor="o-person">{t.contactName}</label>
          <input id="o-person" name="name" className="ui-input" autoComplete="name" maxLength={80} defaultValue={f.name} />
        </div>
        <div className="ui-field">
          <label htmlFor="o-email">{t.contactEmail}</label>
          <input id="o-email" name="email" type="email" className="ui-input" autoComplete="email" required maxLength={200} defaultValue={f.email} aria-describedby="o-email-hint" />
          <span className="ui-hint" id="o-email-hint">{t.contactEmailHint}</span>
        </div>
      </div>
      <div className="ui-field">
        <label htmlFor="o-message">{t.orgMessage}</label>
        <textarea id="o-message" name="message" className="ui-textarea" required minLength={10} maxLength={4000} rows={5} placeholder={t.orgMessagePlaceholder} defaultValue={f.message} />
      </div>
      <div className="ui-trap" aria-hidden="true">
        <label htmlFor="o-website">Website</label>
        <input id="o-website" name="website" tabIndex={-1} autoComplete="off" />
      </div>
      <input type="hidden" name="started" value={started || ""} />
      <input type="hidden" name="pow" value={pow} />
      <p className="ui-hint">{t.contactPrivacy}</p>
      <button type="submit" className="ui-btn" data-variant="primary" disabled={pending}>{pending ? t.contactSending : t.orgSend}</button>
    </form>
  );
}
