import { readFile } from "node:fs/promises";
import { Inject, Injectable, Logger, type OnApplicationBootstrap } from "@nestjs/common";
import { desc, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { releases, type ReleaseNote } from "./operations.schema";

/** Eén commit uit release-log.json (nieuwste eerst), gemaakt in de Deploy-workflow. */
const LogEntry = z.object({ sha: z.string(), date: z.string(), subject: z.string(), note: z.string().default("") });
export type LogEntry = z.infer<typeof LogEntry>;

/** Hoeveel commits een eerste release (of een onbekende vorige versie) hooguit laat zien. */
const FIRST_LIMIT = 30;

/**
 * Notes voor een nieuwe versie: de commits van `sha` terug tot (niet met) `previous`. Een commit met de
 * trailer `Release-note:` toont die Nederlandse tekst; zonder trailer het onderwerp, als technisch.
 */
export function notesBetween(log: LogEntry[], sha: string, previous: string | null): ReleaseNote[] {
  const from = log.findIndex((c) => c.sha === sha);
  if (from < 0) return [];
  const to = previous ? log.findIndex((c) => c.sha === previous) : -1;
  const slice = to > from ? log.slice(from, to) : log.slice(from, from + FIRST_LIMIT);
  return slice.map((c) => ({ sha: c.sha, date: c.date, text: c.note.trim() || c.subject, technical: !c.note.trim() }));
}

@Injectable()
export class ReleasesService implements OnApplicationBootstrap {
  private readonly log = new Logger(ReleasesService.name);
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}

  async onApplicationBootstrap() {
    if (!this.env.BUILD_SHA) return;
    try { await this.record(this.env.BUILD_SHA, await this.readLog()); } catch (e) { this.log.error(`Release vastleggen mislukt: ${e}`); }
  }

  private async readLog(): Promise<LogEntry[]> {
    try { return z.array(LogEntry).parse(JSON.parse(await readFile(this.env.RELEASE_LOG_PATH, "utf8"))); } catch { return []; }
  }

  /** Legt de draaiende versie vast als die anders is dan de laatste. Veilig bij meerdere replica's tegelijk. */
  async record(sha: string, log: LogEntry[]): Promise<"recorded" | "unchanged"> {
    const tenantId = this.env.TENANT_ID;
    return withTenant(this.db, tenantId, async (tx) => {
      await tx.execute(sql`select pg_advisory_xact_lock(hashtext('kleurhoek.releases'))`);
      const [last] = await tx.select().from(releases).where(eq(releases.tenantId, tenantId)).orderBy(desc(releases.startedAt)).limit(1);
      const full = log.find((c) => c.sha.startsWith(sha))?.sha ?? sha;
      if (last?.sha === full) return "unchanged";
      const [seen] = await tx.select({ id: releases.id }).from(releases).where(sql`${releases.tenantId} = ${tenantId} and ${releases.sha} = ${full}`).limit(1);
      const kind = !last ? "first" : seen ? "rollback" : "release";
      const notes = kind === "rollback" ? [] : notesBetween(log, full, last?.sha ?? null);
      await tx.insert(releases).values({ tenantId, sha: full, previousSha: last?.sha ?? null, kind, notes });
      return "recorded";
    });
  }

  list(limit = 50) {
    return withTenant(this.db, this.env.TENANT_ID, (tx) =>
      tx.select({ sha: releases.sha, previousSha: releases.previousSha, kind: releases.kind, notes: releases.notes, startedAt: releases.startedAt })
        .from(releases).where(eq(releases.tenantId, this.env.TENANT_ID)).orderBy(desc(releases.startedAt)).limit(limit));
  }
}
