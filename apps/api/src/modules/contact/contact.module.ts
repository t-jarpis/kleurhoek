import { Inject, Injectable, Logger, Module, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { AdminContactController, ContactController } from "./contact.controller";
import { ContactService } from "./contact.service";

/** Ruimt gesprekken op na de bewaartermijn: bij het opstarten en daarna elke 6 uur. */
@Injectable()
export class ContactPurgeScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(ContactPurgeScheduler.name);
  private timer?: NodeJS.Timeout;
  constructor(private readonly contact: ContactService, @Inject(ENV) private readonly env: Env) {}

  onModuleInit() {
    if (this.env.AGGREGATE_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.run(), 6 * 3_600_000);
    this.timer.unref();
    setTimeout(() => void this.run(), 5000).unref();
  }
  onApplicationShutdown() { clearInterval(this.timer); }

  async run() {
    try {
      const n = await this.contact.purge();
      if (n) this.log.log(`${n} oude gesprekken verwijderd`);
    } catch (e) { this.log.error(`Opruimen mislukt: ${e}`); }
  }
}

/** Domein Contact (ADR 0023): berichten via kanalen en de inbox in het admin panel. */
@Module({ controllers: [ContactController, AdminContactController], providers: [ContactService, ContactPurgeScheduler], exports: [ContactService] })
export class ContactModule {}
