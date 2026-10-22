import { createBff, type Bff } from "@t-jarpis/auth";

/**
 * Inloggen voor beheerders via Zitadel. Alleen accounts uit de beheerorganisatie (met verplichte
 * passkey) komen binnen; de API controleert daarna per verzoek opnieuw het token en de rechten.
 */
let bff: Bff | null | undefined;

export function getBff(): Bff | null {
  if (bff !== undefined) return bff;
  const e = process.env;
  if (!e.OIDC_ISSUER || !e.OIDC_CLIENT_ID || !e.ADMIN_URL || !e.SESSION_SECRET || !e.ADMIN_ORG_ID) return (bff = null);
  const site = e.ADMIN_URL.replace(/\/$/, "");
  bff = createBff({
    issuer: e.OIDC_ISSUER,
    clientId: e.OIDC_CLIENT_ID,
    ...(e.OIDC_CLIENT_SECRET ? { clientSecret: e.OIDC_CLIENT_SECRET } : {}),
    ...(e.OIDC_PROJECT_ID ? { projectId: e.OIDC_PROJECT_ID } : {}),
    organizationId: e.ADMIN_ORG_ID,
    redirectUri: `${site}/auth/callback`,
    postLogoutRedirectUri: `${site}/auth/uitgelogd`,
    sessionSecret: e.SESSION_SECRET,
    cookieName: "kh_admin",
    // Beheerders blijven korter ingelogd dan websitegebruikers: 12 uur.
    sessionMaxAgeSeconds: 12 * 60 * 60,
    insecureDevelopment: process.env.NODE_ENV !== "production" && site.startsWith("http://"),
  });
  return bff;
}

export function sameOrigin(request: Request): boolean {
  const site = request.headers.get("sec-fetch-site");
  if (site) return site === "same-origin";
  const origin = request.headers.get("origin");
  return origin !== null && origin === new URL(request.url).origin;
}
