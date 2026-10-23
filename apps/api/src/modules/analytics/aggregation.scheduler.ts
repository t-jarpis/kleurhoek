import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { AnalyticsService } from "./analytics.service";

/**
 * Werkt de dagtotalen van vandaag en gisteren regelmatig bij. Idempotent, dus veilig met meerdere
 * replica's; later verhuist dit naar een losse worker via Service Bus.
 */
@Injectable()
export class AggregationScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(AggregationScheduler.name);
  private timer?: NodeJS.Timeout;

  constructor(private readonly analytics: AnalyticsService, @Inject(ENV) private readonly env: Env) {}

  onModuleInit() {
    if (this.env.AGGREGATE_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.run(), this.env.AGGREGATE_INTERVAL_MS);
    this.timer.unref();
  }

  onApplicationShutdown() { clearInterval(this.timer); }

  async run(now = new Date()) {
    const today = now.toISOString().slice(0, 10);
    const yesterday = new Date(now.getTime() - 86_400_000).toISOString().slice(0, 10);
    try {
      await this.analytics.aggregateDay(this.env.TENANT_ID, yesterday);
      await this.analytics.aggregateDay(this.env.TENANT_ID, today);
      await this.analytics.purgeRawEvents(this.env.TENANT_ID, now);
    } catch (e) { this.log.error(`Aggregeren mislukt: ${e}`); }
  }
}
