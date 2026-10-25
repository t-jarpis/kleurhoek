import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { CampaignsService } from "./campaigns.service";
import { DeliverabilityService } from "./deliverability/deliverability.service";
import { OutboxService } from "./outbox.service";
import { SubscribersService } from "./subscribers.service";
import { WorkflowsService } from "./workflows.service";

/**
 * Verwerkt mail elke MAIL_INTERVAL_MS (ADR 0037): aanleidingen van workflows, stappen, geplande campagnes en de
 * wachtrij. Alles idempotent; met meerdere replica's voorkomt de unieke sleutel op mails dat er iets dubbel gaat.
 */
@Injectable()
export class MessagingScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger("Mail");
  private timer?: NodeJS.Timeout;
  private busy = false;
  private lastPurge = 0;

  constructor(
    @Inject(ENV) private readonly env: Env, private readonly outbox: OutboxService, private readonly workflows: WorkflowsService,
    private readonly campaigns: CampaignsService, private readonly subscribers: SubscribersService, private readonly delivery: DeliverabilityService,
  ) {}

  onModuleInit() {
    if (this.env.MAIL_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.run(), this.env.MAIL_INTERVAL_MS);
    this.timer.unref();
  }
  onApplicationShutdown() { clearInterval(this.timer); }

  async run(now = new Date()) {
    if (this.busy) return;
    this.busy = true;
    try {
      await this.workflows.tick(now);
      await this.workflows.advance(now);
      await this.campaigns.tick(now);
      const r = await this.outbox.process(now);
      if (r.sent || r.failed) this.log.log(`Mail: ${r.sent} verstuurd, ${r.failed} mislukt`);
      if (now.getTime() - this.lastPurge > 3_600_000) { await this.subscribers.purgePending(now); await this.delivery.purge(now); this.lastPurge = now.getTime(); }
    } catch (e) { this.log.error(`Mail verwerken mislukt: ${e}`); } finally { this.busy = false; }
  }
}
