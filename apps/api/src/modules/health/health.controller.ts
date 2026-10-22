import { Controller, Get, Inject, ServiceUnavailableException } from "@nestjs/common";
import { sql } from "drizzle-orm";
import { DB, type Database } from "../../db/database";
import { SkipRateLimit } from "../operations/rate-limit.guard";

@Controller("health")
@SkipRateLimit()
export class HealthController {
  constructor(@Inject(DB) private readonly db: Database) {}

  @Get()
  async check() {
    try { await this.db.execute(sql`select 1`); } catch { throw new ServiceUnavailableException({ status: "database onbereikbaar" }); }
    return { status: "ok" };
  }
}
