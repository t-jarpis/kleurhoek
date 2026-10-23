import { brandCss, Logo } from "@kleurhoek/theme";
import { PasskeyButton } from "@/components/PasskeyButton";
import { getOrg, logoSrc, type Org } from "@/lib/org";
import { readFlow, type Flow } from "@/lib/state";
import { backToEmail, cancel, resend, skipOffer, startRegister, submitCode, submitEmail, submitRegister, submitVerify, useCode } from "./actions";

export const dynamic = "force-dynamic";
export const metadata = { title: "Inloggen" };

const ERRORS: Record<string, string> = {
  verlopen: "Deze inlogpoging is verlopen. Ga terug naar de site en klik opnieuw op Inloggen.",
  storing: "Inloggen lukt nu even niet. Probeer het over een paar minuten opnieuw.",
};

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ fout?: string }> }) {
  const { fout } = await searchParams;
  const flow = await readFlow();
  const org = flow ? await getOrg(flow.org) : null;
  return (
    <Shell org={org}>
      {!flow ? <Expired text={ERRORS[fout ?? ""] ?? ERRORS.verlopen!} /> : <Step flow={flow} org={org!} />}
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

function Expired({ text }: { text: string }) {
  return <div><h1 id="titel">Opnieuw beginnen</h1><p>{text}</p></div>;
}

function Notice({ flow }: { flow: Flow }) {
  return flow.error ? <p className="ui-error" role="alert">{flow.error}</p> : null;
}

function Foot({ flow }: { flow: Flow }) {
  return (
    <div className="kh-login-foot">
      <form action={cancel} style={{ display: "inline" }}><button type="submit" className="kh-login-link">Terug naar de site</button></form>
      {" · "}<a href={`${flow.back ?? "https://www.kleurhoek.nl"}/privacy`}>Privacy</a>
    </div>
  );
}

function Step({ flow, org }: { flow: Flow; org: Org }) {
  switch (flow.step) {
    case "email":
      return (
        <>
          <div><h1 id="titel">Inloggen</h1><p>Voor ouders en verzorgers: bewaar je boekjes en voorkeuren bij {org.isDefault ? "Kleurhoek" : org.name}.</p></div>
          <form action={submitEmail}>
            <div className="ui-field"><label htmlFor="email">E-mailadres</label>
              <input id="email" name="email" type="email" className="ui-input" autoComplete="username webauthn" inputMode="email" required maxLength={200} defaultValue={flow.email ?? ""} autoFocus aria-invalid={flow.error ? true : undefined} />
            </div>
            <Notice flow={flow} />
            <button type="submit" className="ui-btn" data-variant="primary">Verder</button>
          </form>
          <div className="kh-login-note">Nog geen account? <form action={startRegister} style={{ display: "inline" }}><button type="submit" className="kh-login-link">Maak er een</button></form></div>
          <Foot flow={flow} />
        </>
      );
    case "passkey":
      return (
        <>
          <div><h1 id="titel">Welkom terug</h1><p>Log in met je passkey voor <b>{flow.email}</b>.</p></div>
          <Notice flow={flow} />
          <div className="kh-login-actions">
            <PasskeyButton mode="login" primary label="Inloggen met passkey" />
            <form action={useCode}><button type="submit" className="ui-btn">Stuur me liever een code</button></form>
          </div>
          <div className="kh-login-note"><form action={backToEmail} style={{ display: "inline" }}><button type="submit" className="kh-login-link">Ander e-mailadres</button></form></div>
          <Foot flow={flow} />
        </>
      );
    case "code":
    case "verify": {
      const verify = flow.step === "verify";
      return (
        <>
          <div><h1 id="titel">Vul je code in</h1>
            <p>{verify ? <>We hebben een code gestuurd naar <b>{flow.email}</b> om je adres te bevestigen.</> : <>Als <b>{flow.email}</b> bij ons bekend is, hebben we daar een code naartoe gestuurd. Kijk ook in je ongewenste mail.</>}</p></div>
          <form action={verify ? submitVerify : submitCode}>
            <div className="ui-field"><label htmlFor="code">Code</label>
              <input id="code" name="code" className="ui-input kh-login-code" autoComplete="one-time-code" inputMode="text" required minLength={4} maxLength={12} autoFocus spellCheck={false} aria-invalid={flow.error ? true : undefined} />
            </div>
            <Notice flow={flow} />
            <button type="submit" className="ui-btn" data-variant="primary">{verify ? "Bevestigen" : "Inloggen"}</button>
          </form>
          <div className="kh-login-actions">
            <form action={resend}><button type="submit" className="ui-btn" data-variant="quiet">Stuur een nieuwe code</button></form>
          </div>
          <div className="kh-login-note">
            <form action={backToEmail} style={{ display: "inline" }}><button type="submit" className="kh-login-link">Ander e-mailadres</button></form>
            {!verify && <>{" · "}Nog geen account? <form action={startRegister} style={{ display: "inline" }}><button type="submit" className="kh-login-link">Maak er een</button></form></>}
          </div>
          <Foot flow={flow} />
        </>
      );
    }
    case "register":
      return (
        <>
          <div><h1 id="titel">Account maken</h1><p>Een account is voor ouders en verzorgers. Kinderen kleuren zonder account.</p></div>
          <form action={submitRegister}>
            <div className="ui-field"><label htmlFor="name">Je voornaam</label><input id="name" name="name" className="ui-input" autoComplete="given-name" required maxLength={60} autoFocus /></div>
            <div className="ui-field"><label htmlFor="email">E-mailadres</label><input id="email" name="email" type="email" className="ui-input" autoComplete="email" inputMode="email" required maxLength={200} defaultValue={flow.email ?? ""} /></div>
            <label className="ui-check"><input type="checkbox" name="adult" required /> <span>Ik ben 16 jaar of ouder en ga akkoord met de <a href={`${flow.back ?? "https://www.kleurhoek.nl"}/privacy`}>privacyverklaring</a>.</span></label>
            <Notice flow={flow} />
            <button type="submit" className="ui-btn" data-variant="primary">Account maken</button>
          </form>
          <div className="kh-login-note">Al een account? <form action={backToEmail} style={{ display: "inline" }}><button type="submit" className="kh-login-link">Inloggen</button></form></div>
          <Foot flow={flow} />
        </>
      );
    case "offer":
      return (
        <>
          <div><h1 id="titel">Volgende keer sneller?</h1><p>Met een passkey log je in met je vingerafdruk, gezicht of de pincode van je apparaat. Geen code meer nodig.</p></div>
          <Notice flow={flow} />
          <div className="kh-login-actions">
            <PasskeyButton mode="register" primary label="Passkey maken" />
            <form action={skipOffer}><button type="submit" className="ui-btn">Niet nu</button></form>
          </div>
        </>
      );
  }
}
