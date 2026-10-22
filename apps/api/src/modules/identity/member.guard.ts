import { CanActivate, ExecutionContext, Inject, Injectable, UnauthorizedException } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { ENV, type Env } from "../../config/env";
import { authContext } from "./admin.guard";
import { IdentityService } from "./identity.service";
import { identify, TOKEN_CHECK, type TokenCheck } from "./zitadel";

export interface MemberPrincipal { userId: string; subject: string }
declare module "fastify" { interface FastifyRequest { member?: MemberPrincipal } }

/**
 * Websitegebruikers: een geldig token van de site-organisatie en een actief account. Beheerders
 * gebruiken hun beheeraccount niet op de website; zo blijven de twee werelden gescheiden.
 */
@Injectable()
export class MemberGuard implements CanActivate {
  constructor(@Inject(TOKEN_CHECK) private readonly check: TokenCheck, private readonly identity: IdentityService, @Inject(ENV) private readonly env: Env) {}

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<FastifyRequest>();
    const { authorization, country } = authContext(req);
    const siteOrg = this.env.SITE_ORG_ID;
    const found = await identify(this.check, authorization, (org) => (siteOrg ? org === siteOrg : org !== this.env.ADMIN_ORG_ID));
    if (!found) throw new UnauthorizedException();
    const user = await this.identity.provision(
      { subject: found.identity.subject, organizationId: found.identity.organizationId, kind: "member", country },
      () => this.check.profile(found.token),
    );
    if (user.status !== "active" || user.kind !== "member") throw new UnauthorizedException();
    req.member = { userId: user.id, subject: user.zitadelSub };
    return true;
  }
}
