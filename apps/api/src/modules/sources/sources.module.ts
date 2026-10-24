import { Inject, Injectable, Logger, Module, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { LocalizationModule } from "../localization/localization.module";
import { AdminSourcesController } from "./sources.controller";
import { SourcesService } from "./sources.service";

/**
 * Controleert bronnen die langer dan een dag niet gecontroleerd zijn: kort na het opstarten en daarna
 * elk uur, per keer hooguit 30, één tegelijk met een pauze (we belasten de sites van makers niet).
 * Draait de API op nul (ADR 0021), dan haalt de eerste start alles in.
 */
@Injectable()
export class SourceCheckScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(SourceCheckScheduler.name);
  private timer?: NodeJS.Timeout;
  private running = false;
  constructor(private readonly sources: SourcesService, @Inject(ENV) private readonly env: Env) {}

  onModuleInit() {
    if (this.env.AGGREGATE_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.run(), 3_600_000);
    this.timer.unref();
    setTimeout(() => void this.run(), 30_000).unref();
  }
  onApplicationShutdown() { clearInterval(this.timer); }

  async run(pauseMs = 2000) {
    if (this.running) return;
    this.running = true;
    try {
      for (const id of await this.sources.due(30)) {
        await this.sources.check(id);
        if (pauseMs) await new Promise((r) => setTimeout(r, pauseMs).unref());
      }
    } catch (e) { this.log.error(`Bronnencontrole mislukt: ${e}`); }
    finally { this.running = false; }
  }
}

/** Domein Bronnen (ADR 0024): de Bronnengids met links naar kleurplaten bij de makers zelf. */
@Module({ imports: [LocalizationModule], controllers: [AdminSourcesController], providers: [SourcesService, SourceCheckScheduler], exports: [SourcesService] })
export class SourcesModule {}
