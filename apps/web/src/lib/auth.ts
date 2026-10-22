import "server-only";
import { createBff, type Bff } from "@t-jarpis/auth";
export { sameOrigin } from "./same-origin";

/**
 * Inloggen voor websitegebruikers (ouders, leerkrachten) via Zitadel, met het BFF-patroon: tokens
 * blijven op de server, de browser krijgt alleen een versleutelde HttpOnly-cookie. Zonder
 * configuratie staat inloggen uit en tonen we geen knop.
 */
let bff: Bff | null | undefined;

export function getBff(): Bff | null {
  if (bff !== undefined) return bff;
  const e = process.env;
  if (!e.OIDC_ISSUER || !e.OIDC_CLIENT_ID || !e.SITE_URL || !e.SESSION_SECRET) return (bff = null);
  const site = e.SITE_URL.replace(/\/$/, "");
  bff = createBff({
    issuer: e.OIDC_ISSUER,
    clientId: e.OIDC_CLIENT_ID,
    ...(e.OIDC_CLIENT_SECRET ? { clientSecret: e.OIDC_CLIENT_SECRET } : {}),
    ...(e.OIDC_PROJECT_ID ? { projectId: e.OIDC_PROJECT_ID } : {}),
    ...(e.OIDC_ORG_ID ? { organizationId: e.OIDC_ORG_ID } : {}),
    redirectUri: `${site}/auth/callback`,
    postLogoutRedirectUri: `${site}/`,
    sessionSecret: e.SESSION_SECRET,
    cookieName: "kh_session",
    insecureDevelopment: process.env.NODE_ENV !== "production" && site.startsWith("http://"),
  });
  return bff;
}

export const noStore = { "cache-control": "private, no-store" };

/** Zet een eventueel ververste sessiecookie op het antwoord. */
export function withCookie(res: Response, setCookie: string | undefined): Response {
  if (setCookie) res.headers.append("set-cookie", setCookie);
  return res;
}
