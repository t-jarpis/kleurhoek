import { brandCss, Logo } from "@kleurhoek/theme";
import { PasskeyButton } from "@/components/PasskeyButton";
import { getOrg, logoSrc, type Org } from "@/lib/org";
import { headers } from "next/headers";
import { pickLanguage, t as messages } from "@/lib/i18n";
import type { LoginMessages } from "@/lib/messages";
import { readFlow, type Flow } from "@/lib/state";
import { backToEmail, cancel, resend, skipOffer, startRegister, submitCode, submitEmail, submitRegister, submitVerify, useCode } from "./actions";

export const dynamic = "force-dynamic";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ fout?: string }> }) {
  const { fout } = await searchParams;
  const flow = await readFlow();
  const org = flow ? await getOrg(flow.org) : null;
  // Zonder flow (verlopen) kennen we de taal niet uit het verzoek: dan die van de browser.
  const t = messages(flow?.lang ?? pickLanguage(undefined, (await headers()).get("accept-language")));
  return (
    <Shell org={org}>
      {!flow ? <Expired t={t} text={fout === "storing" ? t.errOutage : t.errExpired} /> : <Step flow={flow} org={org!} t={t} />}
    </Shell>
  );
}

/** Kaart in de huisstijl van de organisatie: kleuren, lettertype, logo (ADR 0017). */
function Shell({ org, children }: { org: Org | null; children: React.ReactNode }) {
  const font = org?.brand.font;
  const logo = org ? logoSrc(org) : null;
  return (
    <div className="kh-login-page" {...(font ? { "data-kh-font": font } : {})}>
      {org && brandCss(org.brand.colors) ? <style>{brandCss(org.brand.colors)}</style> : null}
      <main className="kh-login" aria-labelledby="titel">
        <span aria-label={org?.name ?? "Kleurhoek"} role="img"><Logo size={26} wordmark={org?.brand.wordmark ?? null} image={logo} /></span>
        {children}
      </main>
    </div>
  );
}

function Expired({ text, t }: { text: string; t: LoginMessages }) {
  return <div><h1 id="titel">{t.expiredTitle}</h1><p>{text}</p></div>;
}

function Notice({ flow }: { flow: Flow }) {
  return flow.error ? <p className="ui-error" role="alert">{flow.error}</p> : null;
}

function Foot({ flow, t }: { flow: Flow; t: LoginMessages }) {
  return (
    <div className="kh-login-foot">
      <form action={cancel} style={{ display: "inline" }}><button type="submit" className="kh-login-link">{t.backToSite}</button></form>
      {" · "}<a href={`${flow.back ?? "https://www.kleurhoek.nl"}/privacy`}>{t.privacy}</a>
    </div>
  );
}

function Step({ flow, org, t }: { flow: Flow; org: Org; t: LoginMessages }) {
  switch (flow.step) {
    case "email":
      return (
        <>
          <div><h1 id="titel">{t.title}</h1><p>{t.emailIntro(org.isDefault ? "Kleurhoek" : org.name)}</p></div>
          <form action={submitEmail}>
            <div className="ui-field"><label htmlFor="email">{t.email}</label>
              <input id="email" name="email" type="email" className="ui-input" autoComplete="username webauthn" inputMode="email" required maxLength={200} defaultValue={flow.email ?? ""} autoFocus aria-invalid={flow.error ? true : undefined} />
            </div>
            <Notice flow={flow} />
            <button type="submit" className="ui-btn" data-variant="primary">{t.next}</button>
          </form>
          <div className="kh-login-note">{t.noAccount} <form action={startRegister} style={{ display: "inline" }}><button type="submit" className="kh-login-link">{t.makeOne}</button></form></div>
          {/* Inloggen via school, opvang of bibliotheek (SSO per organisatie): nog niet beschikbaar, wel zichtbaar. */}
          <div className="kh-login-or" aria-hidden="true">{t.or}</div>
          <div className="kh-login-org">
            <button type="button" className="ui-btn" disabled aria-describedby="org-hint">{t.orgLogin} <span className="ui-badge">{t.soon}</span></button>
            <p className="kh-login-note" id="org-hint">{t.orgLoginHint}</p>
          </div>
          <Foot flow={flow} t={t} />
        </>
      );
    case "passkey":
      return (
        <>
          <div><h1 id="titel">{t.welcomeBack}</h1><p>{t.passkeyFor} <b>{flow.email}</b>.</p></div>
          <Notice flow={flow} />
          <div className="kh-login-actions">
            <PasskeyButton mode="login" primary label={t.loginPasskey} t={t} />
            <form action={useCode}><button type="submit" className="ui-btn">{t.ratherCode}</button></form>
          </div>
          <div className="kh-login-note"><form action={backToEmail} style={{ display: "inline" }}><button type="submit" className="kh-login-link">{t.otherEmail}</button></form></div>
          <Foot flow={flow} t={t} />
        </>
      );
    case "code":
    case "verify": {
      const verify = flow.step === "verify";
      return (
        <>
          <div><h1 id="titel">{t.enterCode}</h1>
            <p>{verify ? <>{t.codeSentVerify} <b>{flow.email}</b></> : <><b>{flow.email}</b>: {t.codeSentLogin}</>}</p></div>
          <form action={verify ? submitVerify : submitCode}>
            <div className="ui-field"><label htmlFor="code">{t.code}</label>
              <input id="code" name="code" className="ui-input kh-login-code" autoComplete="one-time-code" inputMode="text" required minLength={4} maxLength={12} autoFocus spellCheck={false} aria-invalid={flow.error ? true : undefined} />
            </div>
            <Notice flow={flow} />
            <button type="submit" className="ui-btn" data-variant="primary">{verify ? t.confirm : t.login}</button>
          </form>
          <div className="kh-login-actions">
            <form action={resend}><button type="submit" className="ui-btn" data-variant="quiet">{t.resend}</button></form>
          </div>
          <div className="kh-login-note">
            <form action={backToEmail} style={{ display: "inline" }}><button type="submit" className="kh-login-link">{t.otherEmail}</button></form>
            {!verify && <>{" · "}{t.noAccount} <form action={startRegister} style={{ display: "inline" }}><button type="submit" className="kh-login-link">{t.makeOne}</button></form></>}
          </div>
          <Foot flow={flow} t={t} />
        </>
      );
    }
    case "register":
      return (
        <>
          <div><h1 id="titel">{t.createTitle}</h1><p>{t.createIntro}</p></div>
          <form action={submitRegister}>
            <div className="ui-field"><label htmlFor="name">{t.firstName}</label><input id="name" name="name" className="ui-input" autoComplete="given-name" required maxLength={60} autoFocus /></div>
            <div className="ui-field"><label htmlFor="email">{t.email}</label><input id="email" name="email" type="email" className="ui-input" autoComplete="email" inputMode="email" required maxLength={200} defaultValue={flow.email ?? ""} /></div>
            <label className="ui-check"><input type="checkbox" name="adult" required /> <span>{t.adultBefore} <a href={`${flow.back ?? "https://www.kleurhoek.nl"}/privacy`}>{t.privacyStatement}</a>.</span></label>
            <Notice flow={flow} />
            <button type="submit" className="ui-btn" data-variant="primary">{t.create}</button>
          </form>
          <div className="kh-login-note">{t.haveAccount} <form action={backToEmail} style={{ display: "inline" }}><button type="submit" className="kh-login-link">{t.login}</button></form></div>
          <Foot flow={flow} t={t} />
        </>
      );
    case "offer":
      return (
        <>
          <div><h1 id="titel">{t.offerTitle}</h1><p>{t.offerText}</p></div>
          <Notice flow={flow} />
          <div className="kh-login-actions">
            <PasskeyButton mode="register" primary label={t.makePasskey} t={t} />
            <form action={skipOffer}><button type="submit" className="ui-btn">{t.notNow}</button></form>
          </div>
        </>
      );
  }
}
