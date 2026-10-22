import { Global, Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { AdminRateLimitsController } from "./admin-rate-limits.controller";
import { RateLimitGuard } from "./rate-limit.guard";
import { RateLimitService } from "./rate-limit.service";
import { MemoryRateLimitStore, RATE_LIMIT_STORE } from "./rate-limit.store";

@Global()
@Module({
  controllers: [AdminRateLimitsController],
  providers: [
    { provide: RATE_LIMIT_STORE, useClass: MemoryRateLimitStore },
    RateLimitService,
    { provide: APP_GUARD, useClass: RateLimitGuard },
  ],
  exports: [RateLimitService],
})
export class OperationsModule {}
