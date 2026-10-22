import { Global, Module } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { ADMIN_AUTHENTICATOR, AdminGuard, DenyAllAuthenticator, DevTokenAuthenticator } from "./admin.guard";
import { AuditService } from "./audit.service";

@Global()
@Module({
  providers: [{
    provide: ADMIN_AUTHENTICATOR,
    inject: [ENV],
    // Tot @t-jarpis/auth gekoppeld is: alles dicht, behalve lokaal met een expliciete dev-token.
    useFactory: (env: Env) => env.NODE_ENV === "development" && env.ADMIN_DEV_TOKEN ? new DevTokenAuthenticator(env.ADMIN_DEV_TOKEN) : new DenyAllAuthenticator(),
  }, AdminGuard, AuditService],
  exports: [ADMIN_AUTHENTICATOR, AdminGuard, AuditService],
})
export class IdentityModule {}
