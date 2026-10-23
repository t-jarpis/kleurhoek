/**
 * Omzetten tussen de JSON van Zitadel (base64url-tekst) en de WebAuthn-API van de browser (ArrayBuffers).
 * Zitadel geeft de opties soms als { publicKey: {...} }; beide vormen worden geaccepteerd.
 */
type Json = Record<string, unknown>;

export const fromB64 = (s: string): ArrayBuffer => {
  const b = atob(s.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(s.length / 4) * 4, "="));
  const out = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) out[i] = b.charCodeAt(i);
  return out.buffer;
};
export const toB64 = (buf: ArrayBuffer | null): string | null => {
  if (!buf) return null;
  let s = "";
  for (const byte of new Uint8Array(buf)) s += String.fromCharCode(byte);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
};

const unwrap = (o: Json): Json => ((o.publicKey as Json | undefined) ?? o);
const creds = (list: unknown) => ((list as Json[] | undefined) ?? []).map((c) => ({ ...c, id: fromB64(String(c.id)) }));

export function requestOptions(o: Json): PublicKeyCredentialRequestOptions {
  const p = unwrap(o);
  return { ...(p as object), challenge: fromB64(String(p.challenge)), allowCredentials: creds(p.allowCredentials) } as PublicKeyCredentialRequestOptions;
}

export function creationOptions(o: Json): PublicKeyCredentialCreationOptions {
  const p = unwrap(o);
  const user = p.user as Json;
  return {
    ...(p as object), challenge: fromB64(String(p.challenge)),
    user: { ...user, id: fromB64(String(user.id)) }, excludeCredentials: creds(p.excludeCredentials),
  } as PublicKeyCredentialCreationOptions;
}

export function assertionJson(c: PublicKeyCredential): Json {
  const r = c.response as AuthenticatorAssertionResponse;
  return { id: c.id, rawId: toB64(c.rawId), type: c.type, response: {
    authenticatorData: toB64(r.authenticatorData), clientDataJSON: toB64(r.clientDataJSON), signature: toB64(r.signature), userHandle: toB64(r.userHandle),
  } };
}

export function attestationJson(c: PublicKeyCredential): Json {
  const r = c.response as AuthenticatorAttestationResponse;
  return { id: c.id, rawId: toB64(c.rawId), type: c.type, response: { attestationObject: toB64(r.attestationObject), clientDataJSON: toB64(r.clientDataJSON) } };
}
