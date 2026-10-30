import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { SocialService } from "./social.service";

/** Elke paar minuten: voorstellen maken (één keer per dag), goedgekeurde posts plaatsen, de ochtendmail (ADR 0063). */
@Injectable()
export class SocialScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(SocialScheduler.name);
  private timer?: NodeJS.Timeout;
  private busy = false;
  constructor(private readonly social: SocialService, @Inject(ENV) private readonly env: Env) {}
  onModuleInit() {
    if (this.env.SOCIAL_INTERVAL_MS === 0) return;
    this.timer = setInterval(() => void this.run(), this.env.SOCIAL_INTERVAL_MS);
    this.timer.unref();
  }
  onApplicationShutdown() { clearInterval(this.timer); }
  private async run() {
    if (this.busy) return;
    this.busy = true;
    try { await this.social.tick(); } catch (e) { this.log.error(`Social mislukt: ${e}`); } finally { this.busy = false; }
  }
}
