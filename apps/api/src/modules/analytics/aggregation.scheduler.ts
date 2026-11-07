import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { AnalyticsService } from "./analytics.service";
import { WishesService } from "./wishes.service";

/**
 * Werkt de dagtotalen bij: bij het opstarten en daarna regelmatig. Elke keer vandaag plus alle dagen die
 * achterlopen, zodat er na een periode op nul (ADR 0021) niets verloren gaat. Idempotent, dus veilig
 * met meerdere replica's.
 */
@Injectable()
export class AggregationScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(AggregationScheduler.name);
  private timer?: NodeJS.Timeout;

  constructor(private readonly analytics: AnalyticsService, private readonly wishes: WishesService, @Inject(ENV) private readonly env: Env) {}

  onModuleInit() {
    if (this.env.AGGREGATE_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.run(), this.env.AGGREGATE_INTERVAL_MS);
    this.timer.unref();
    setTimeout(() => void this.run(), 1000).unref();
  }

  onApplicationShutdown() { clearInterval(this.timer); }

  async run(now = new Date()) {
    const today = now.toISOString().slice(0, 10);
    try {
      const days = new Set([...(await this.analytics.staleDays(this.env.TENANT_ID)), today]);
      for (const day of [...days].sort()) await this.analytics.aggregateDay(this.env.TENANT_ID, day);
      await this.analytics.anonymizeRawEvents(this.env.TENANT_ID, now);
      await this.wishes.anonymize(this.env.TENANT_ID, now);
    } catch (e) { this.log.error(`Aggregeren mislukt: ${e}`); }
  }
}
