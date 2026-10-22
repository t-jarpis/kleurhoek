import { Global, Module } from "@nestjs/common";
import { ADMIN_AUTHENTICATOR, AdminGuard, DenyAllAuthenticator } from "./admin.guard";
import { AuditService } from "./audit.service";

@Global()
@Module({
  providers: [{ provide: ADMIN_AUTHENTICATOR, useClass: DenyAllAuthenticator }, AdminGuard, AuditService],
  exports: [ADMIN_AUTHENTICATOR, AdminGuard, AuditService],
})
export class IdentityModule {}
