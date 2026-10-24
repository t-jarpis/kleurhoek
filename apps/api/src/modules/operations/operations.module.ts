import { Global, Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { AdminRateLimitsController } from "./admin-rate-limits.controller";
import { RateLimitGuard } from "./rate-limit.guard";
import { RateLimitService } from "./rate-limit.service";
import { MemoryRateLimitStore, RATE_LIMIT_STORE } from "./rate-limit.store";
import { AdminSiteAccessController, InternalSiteAccessController } from "./site-access.controller";
import { SiteAccessService } from "./site-access.service";
import { AdminReleasesController } from "./releases.controller";
import { ReleasesService } from "./releases.service";

@Global()
@Module({
  controllers: [AdminRateLimitsController, AdminSiteAccessController, InternalSiteAccessController, AdminReleasesController],
  providers: [
    { provide: RATE_LIMIT_STORE, useClass: MemoryRateLimitStore },
    RateLimitService,
    SiteAccessService,
    ReleasesService,
    { provide: APP_GUARD, useClass: RateLimitGuard },
  ],
  exports: [RateLimitService],
})
export class OperationsModule {}
