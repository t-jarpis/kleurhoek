import "server-only";

/**
 * De v2-API's van Zitadel die de inlogpagina gebruikt (ADR 0018): OIDC (auth request afronden),
 * sessies (controles: gebruiker, e-mailcode, passkey) en gebruikers (aanmaken, e-mail bevestigen,
 * e-mailcode en passkey toevoegen). Alles met het token van de service user `kleurhoek-login`,
 * die de rol IAM_LOGIN_CLIENT heeft. Eigen code op de openbare API, niet de login-app van Zitadel.
 */
const BASE = () => (process.env.ZITADEL_URL ?? "").replace(/\/$/, "");

export class ZitadelError extends Error {
  constructor(readonly status: number, readonly code: number | undefined, message: string) { super(message); }
  get notFound() { return this.status === 404 || this.code === 5; }
  get exists() { return this.status === 409 || this.code === 6; }
  get invalid() { return this.status === 400 || this.code === 3 || this.code === 9; }
}

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  const token = process.env.ZITADEL_LOGIN_TOKEN;
  if (!BASE() || !token) throw new Error("ZITADEL_URL en ZITADEL_LOGIN_TOKEN zijn nodig");
  const res = await fetch(`${BASE()}${path}`, {
    method, cache: "no-store", signal: AbortSignal.timeout(10_000),
    headers: { authorization: `Bearer ${token}`, accept: "application/json", ...(body !== undefined ? { "content-type": "application/json" } : {}) },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });
  const text = await res.text();
  const json = text ? (JSON.parse(text) as Record<string, unknown>) : {};
  if (!res.ok) throw new ZitadelError(res.status, json.code as number | undefined, String(json.message ?? res.statusText));
  return json as T;
}

export interface AuthRequest { id: string; clientId: string; redirectUri: string; loginHint?: string; scope?: string[]; uiLocales?: string[] }
export type AuthMethod = "AUTHENTICATION_METHOD_TYPE_PASSKEY" | "AUTHENTICATION_METHOD_TYPE_OTP_EMAIL" | "AUTHENTICATION_METHOD_TYPE_IDP" | string;
export interface FoundUser { userId: string; email: string; verified: boolean }
type Json = Record<string, unknown>;

/** RP-ID voor passkeys: het hoofddomein, zodat een passkey op alle subdomeinen werkt. */
export const passkeyDomain = () => process.env.PASSKEY_DOMAIN ?? "localhost";

export const zitadel = {
  authRequest: async (id: string) => (await call<{ authRequest: AuthRequest }>("GET", `/v2/oidc/auth_requests/${encodeURIComponent(id)}`)).authRequest,
  /** Koppelt de sessie aan het auth request; daarna naar callbackUrl (terug naar de site met een code). */
  finalize: async (id: string, sessionId: string, sessionToken: string) =>
    (await call<{ callbackUrl: string }>("POST", `/v2/oidc/auth_requests/${encodeURIComponent(id)}`, { session: { sessionId, sessionToken } })).callbackUrl,
  /** Inloggen afbreken: de site krijgt error=access_denied terug. */
  deny: async (id: string) =>
    (await call<{ callbackUrl: string }>("POST", `/v2/oidc/auth_requests/${encodeURIComponent(id)}`, { error: { error: "ERROR_REASON_ACCESS_DENIED", errorDescription: "Inloggen afgebroken" } })).callbackUrl,

  findUser: async (email: string, orgId: string): Promise<FoundUser | null> => {
    const r = await call<{ result?: { userId: string; human?: { email?: { email: string; isVerified?: boolean } } }[] }>("POST", "/v2/users", {
      query: { limit: 2 },
      queries: [
        { emailQuery: { emailAddress: email, method: "TEXT_QUERY_METHOD_EQUALS_IGNORE_CASE" } },
        { organizationIdQuery: { organizationId: orgId } },
        { typeQuery: { type: "TYPE_HUMAN" } },
      ],
    });
    const u = r.result?.length === 1 ? r.result[0] : undefined;
    return u?.human?.email ? { userId: u.userId, email: u.human.email.email, verified: !!u.human.email.isVerified } : null;
  },
  methods: async (userId: string) => (await call<{ authMethodTypes?: AuthMethod[] }>("GET", `/v2/users/${userId}/authentication_methods`)).authMethodTypes ?? [],
  addHuman: async (orgId: string, email: string, name: string, language = "nl") =>
    (await call<{ userId: string }>("POST", "/v2/users/human", {
      organization: { orgId },
      profile: { givenName: name, familyName: "-", displayName: name, preferredLanguage: language },
      email: { email, sendCode: {} },
    })).userId,
  verifyEmail: (userId: string, code: string) => call<Json>("POST", `/v2/users/${userId}/email/verify`, { verificationCode: code }),
  resendEmailCode: (userId: string) => call<Json>("POST", `/v2/users/${userId}/email/resend`, { sendCode: {} }),
  addOtpEmail: (userId: string) => call<Json>("POST", `/v2/users/${userId}/otp_email`, {}),

  createSession: (userId: string, challenges?: Json) =>
    call<{ sessionId: string; sessionToken: string; challenges?: Json }>("POST", "/v2/sessions", {
      checks: { user: { userId } }, ...(challenges ? { challenges } : {}), lifetime: "86400s",
    }),
  setSession: (sessionId: string, body: { checks?: Json; challenges?: Json }) =>
    call<{ sessionToken: string; challenges?: Json }>("PATCH", `/v2/sessions/${sessionId}`, body),

  passkeyRegistration: async (userId: string) => {
    const link = await call<{ code: { id: string; code: string } }>("POST", `/v2/users/${userId}/passkeys/registration_link`, { returnCode: {} });
    return call<{ passkeyId: string; publicKeyCredentialCreationOptions: Json }>("POST", `/v2/users/${userId}/passkeys`, {
      code: link.code, authenticator: "PASSKEY_AUTHENTICATOR_UNSPECIFIED", domain: passkeyDomain(),
    });
  },
  verifyPasskey: (userId: string, passkeyId: string, credential: Json, name: string) =>
    call<Json>("POST", `/v2/users/${userId}/passkeys/${passkeyId}`, { publicKeyCredential: credential, passkeyName: name }),
};

export const otpChallenge = { otpEmail: { sendCode: {} } };
export const passkeyChallenge = () => ({ webAuthN: { domain: passkeyDomain(), userVerificationRequirement: "USER_VERIFICATION_REQUIREMENT_REQUIRED" } });
