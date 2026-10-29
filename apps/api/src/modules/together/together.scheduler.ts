import { Inject, Injectable, Logger, type OnApplicationShutdown, type OnModuleInit } from "@nestjs/common";
import { ENV, type Env } from "../../config/env";
import { TogetherService } from "./together.service";

/** Ruimt kamers op waar al een half uur niemand meer is (ADR 0060). Idempotent, dus veilig met meerdere replica's. */
@Injectable()
export class TogetherScheduler implements OnModuleInit, OnApplicationShutdown {
  private readonly log = new Logger(TogetherScheduler.name);
  private timer?: NodeJS.Timeout;
  constructor(private readonly together: TogetherService, @Inject(ENV) private readonly env: Env) {}
  onModuleInit() {
    if (this.env.TOGETHER_CLEANUP_MS === 0) return;
    this.timer = setInterval(() => void this.together.cleanup().catch((e) => this.log.error(`Opruimen mislukt: ${e}`)), this.env.TOGETHER_CLEANUP_MS);
    this.timer.unref();
  }
  onApplicationShutdown() { clearInterval(this.timer); }
}
