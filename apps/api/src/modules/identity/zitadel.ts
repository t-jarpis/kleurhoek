import { Logger } from "@nestjs/common";
import { bearerToken, fetchUserInfo, createTokenVerifier, TokenVerificationError, type VerifiedIdentity } from "@t-jarpis/auth";
import type { AdminAuthenticator, AdminPrincipal, AuthContext } from "./admin.guard";
import type { IdentityService, Profile } from "./identity.service";

/** Controleert access tokens van Zitadel en haalt het profiel op. Eén instantie per proces (JWKS wordt gecachet). */
export interface TokenCheck {
  verify(token: string): Promise<VerifiedIdentity>;
  profile(token: string): Promise<Profile | null>;
}
export const TOKEN_CHECK = Symbol("TOKEN_CHECK");

export function zitadelTokenCheck(issuer: string, audience: string): TokenCheck {
  const verify = createTokenVerifier({ issuer, audience });
  return {
    verify,
    async profile(token) {
      const info = await fetchUserInfo(issuer, token);
      return info ? { name: info.name, email: info.email, locale: info.locale } : null;
    },
  };
}

/** Zonder Zitadel-configuratie: elk token is ongeldig. */
export const rejectAllTokens: TokenCheck = {
  verify: () => Promise.reject(new TokenVerificationError("invalid")),
  profile: () => Promise.resolve(null),
};

const log = new Logger("Identity");

/** Gedeelde stap voor beheerders en websitegebruikers: token controleren en organisatie afdwingen. */
export async function identify(check: TokenCheck, authorization: string | undefined, allowedOrg: (org: string) => boolean) {
  const token = bearerToken(authorization);
  if (!token) return null;
  let identity: VerifiedIdentity;
  try {
    identity = await check.verify(token);
  } catch (error) {
    if (!(error instanceof TokenVerificationError)) log.error(error);
    return null;
  }
  if (!identity.organizationId || !allowedOrg(identity.organizationId)) return null;
  return { token, identity: identity as VerifiedIdentity & { organizationId: string } };
}

/** Beheerders: token van de beheerorganisatie, actieve gebruiker, rechten uit de eigen rollen. */
export class ZitadelAdminAuthenticator implements AdminAuthenticator {
  constructor(private readonly check: TokenCheck, private readonly identity: IdentityService, private readonly adminOrgId: string) {}

  async authenticate(ctx: AuthContext): Promise<AdminPrincipal | null> {
    const found = await identify(this.check, ctx.authorization, (org) => org === this.adminOrgId);
    if (!found) return null;
    const user = await this.identity.provision(
      { subject: found.identity.subject, organizationId: found.identity.organizationId, kind: "admin", country: ctx.country },
      () => this.check.profile(found.token),
    );
    if (user.status !== "active" || user.kind !== "admin") return null;
    return { userId: user.id, subject: user.zitadelSub, permissions: await this.identity.permissionsOf(user.id) };
  }
}
