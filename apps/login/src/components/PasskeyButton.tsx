"use client";
import { useEffect, useState } from "react";
import { assertionJson, attestationJson, creationOptions, requestOptions } from "@/lib/webauthn";

async function post(body: object): Promise<Record<string, unknown>> {
  const res = await fetch("/api/passkey", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  const json = (await res.json().catch(() => ({}))) as Record<string, unknown>;
  if (!res.ok) throw new Error(String(json.message ?? "Dat lukte niet."));
  return json;
}

/** Inloggen met een passkey, of er een maken na het inloggen. Zonder ondersteuning in de browser: niets. */
export function PasskeyButton({ mode, primary = false, label }: { mode: "login" | "register"; primary?: boolean; label: string }) {
  const [supported, setSupported] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { setSupported(typeof window !== "undefined" && "PublicKeyCredential" in window); }, []);
  if (!supported) return null;

  async function run() {
    setBusy(true); setError(null);
    try {
      if (mode === "login") {
        const { options } = await post({ action: "login-start" });
        const cred = (await navigator.credentials.get({ publicKey: requestOptions(options as Record<string, unknown>) })) as PublicKeyCredential | null;
        if (!cred) throw new Error("Geen passkey gekozen.");
        const { redirect } = await post({ action: "login-finish", credential: assertionJson(cred) });
        window.location.assign(String(redirect));
      } else {
        const { options, passkeyId } = await post({ action: "register-start" });
        const cred = (await navigator.credentials.create({ publicKey: creationOptions(options as Record<string, unknown>) })) as PublicKeyCredential | null;
        if (!cred) throw new Error("Geen passkey gemaakt.");
        const { redirect } = await post({ action: "register-finish", passkeyId, credential: attestationJson(cred) });
        window.location.assign(String(redirect));
      }
    } catch (e) {
      setBusy(false);
      setError(e instanceof DOMException && e.name === "NotAllowedError" ? "Afgebroken. Probeer het opnieuw of kies een andere manier." : (e as Error).message);
    }
  }

  return (
    <>
      <button type="button" className="ui-btn" data-variant={primary ? "primary" : undefined} onClick={run} disabled={busy} aria-busy={busy || undefined}>
        {busy ? "Even geduld…" : label}
      </button>
      {error && <p className="ui-error" role="alert">{error}</p>}
    </>
  );
}
