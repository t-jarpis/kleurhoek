import { Global, Logger, Module } from "@nestjs/common";
import { ENV, oidcEnabled, type Env } from "../../config/env";
import { ADMIN_AUTHENTICATOR, AdminGuard, DenyAllAuthenticator, DevTokenAuthenticator, type AdminAuthenticator } from "./admin.guard";
import { AdminUsersController } from "./admin-users.controller";
import { AuditService } from "./audit.service";
import { IdentityService } from "./identity.service";
import { MeController } from "./me.controller";
import { MemberGuard } from "./member.guard";
import { rejectAllTokens, TOKEN_CHECK, zitadelTokenCheck, ZitadelAdminAuthenticator, type TokenCheck } from "./zitadel";

@Global()
@Module({
  controllers: [MeController, AdminUsersController],
  providers: [
    {
      provide: TOKEN_CHECK,
      inject: [ENV],
      useFactory: (env: Env): TokenCheck => oidcEnabled(env) ? zitadelTokenCheck(env.OIDC_ISSUER, env.OIDC_AUDIENCE) : rejectAllTokens,
    },
    {
      provide: ADMIN_AUTHENTICATOR,
      inject: [ENV, TOKEN_CHECK, IdentityService],
      useFactory: (env: Env, check: TokenCheck, identity: IdentityService): AdminAuthenticator => {
        if (oidcEnabled(env)) return new ZitadelAdminAuthenticator(check, identity, env.ADMIN_ORG_ID);
        // Lokaal zonder Zitadel: alleen met een expliciete dev-token. Anders alles dicht.
        if (env.NODE_ENV === "development" && env.ADMIN_DEV_TOKEN) {
          new Logger("Identity").warn("Admin draait met ADMIN_DEV_TOKEN: alleen voor lokaal gebruik");
          return new DevTokenAuthenticator(env.ADMIN_DEV_TOKEN);
        }
        return new DenyAllAuthenticator();
      },
    },
    AdminGuard, MemberGuard, AuditService, IdentityService,
  ],
  exports: [ADMIN_AUTHENTICATOR, TOKEN_CHECK, AdminGuard, MemberGuard, AuditService, IdentityService],
})
export class IdentityModule {}
