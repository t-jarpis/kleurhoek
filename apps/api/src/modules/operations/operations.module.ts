import { Global, Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { AdminRateLimitsController } from "./admin-rate-limits.controller";
import { RateLimitGuard } from "./rate-limit.guard";
import { RateLimitService } from "./rate-limit.service";
import { MemoryRateLimitStore, RATE_LIMIT_STORE } from "./rate-limit.store";
import { AdminSiteAccessController, InternalSiteAccessController } from "./site-access.controller";
import { SiteAccessService } from "./site-access.service";

@Global()
@Module({
  controllers: [AdminRateLimitsController, AdminSiteAccessController, InternalSiteAccessController],
  providers: [
    { provide: RATE_LIMIT_STORE, useClass: MemoryRateLimitStore },
    RateLimitService,
    SiteAccessService,
    { provide: APP_GUARD, useClass: RateLimitGuard },
  ],
  exports: [RateLimitService],
})
export class OperationsModule {}
