import "server-only";
import { createBff, isLocalUrl, type Bff } from "@t-jarpis/auth";
import { domainForHost, siteDomains } from "./sites";
export { sameOrigin } from "./same-origin";

/**
 * Inloggen voor websitegebruikers (ouders, leerkrachten) via Zitadel, met het BFF-patroon: tokens
 * blijven op de server, de browser krijgt alleen een versleutelde HttpOnly-cookie. Zonder
 * configuratie staat inloggen uit en tonen we geen knop.
 */
const cache = new Map<string, Bff | null>();

/**
 * Het adres waarop de bezoeker de site gebruikt: kleurhoek.be en .com hebben elk hun eigen terugkeeradres en
 * sessiecookie (ADR 0040). Anders SITE_URL.
 */
function siteOrigin(request: Request | undefined, site: string): string {
  const domains = siteDomains();
  const key = domainForHost(request?.headers.get("x-kh-site-host") ?? null, domains);
  return key && domains ? domains[key] : site;
}

export function getBff(request?: Request): Bff | null {
  const e = process.env;
  if (!e.OIDC_ISSUER || !e.OIDC_CLIENT_ID || !e.SITE_URL || !e.SESSION_SECRET) return null;
  const site = siteOrigin(request, e.SITE_URL.replace(/\/$/, ""));
  if (cache.has(site)) return cache.get(site)!;
  const bff = createBff({
    issuer: e.OIDC_ISSUER,
    clientId: e.OIDC_CLIENT_ID,
    ...(e.OIDC_CLIENT_SECRET ? { clientSecret: e.OIDC_CLIENT_SECRET } : {}),
    ...(e.OIDC_PROJECT_ID ? { projectId: e.OIDC_PROJECT_ID } : {}),
    ...(e.OIDC_ORG_ID ? { organizationId: e.OIDC_ORG_ID } : {}),
    redirectUri: `${site}/auth/callback`,
    postLogoutRedirectUri: `${site}/`,
    sessionSecret: e.SESSION_SECRET,
    cookieName: "kh_session",
    // Alleen als alles op deze machine draait (docker compose, pnpm dev): http en cookies zonder Secure.
    insecureDevelopment: isLocalUrl(site) && isLocalUrl(e.OIDC_ISSUER),
  });
  cache.set(site, bff);
  return bff;
}

export const noStore = { "cache-control": "private, no-store" };

/** Zet eventueel ververste sessiecookies op het antwoord (een sessie kan over meerdere cookies verdeeld zijn). */
export function withCookie(res: Response, setCookies: string[] | undefined): Response {
  for (const c of setCookies ?? []) res.headers.append("set-cookie", c);
  return res;
}
