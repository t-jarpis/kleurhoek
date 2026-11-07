import { Inject, Injectable, type OnModuleInit } from "@nestjs/common";
import { and, eq, lt, sql } from "drizzle-orm";
import { z } from "zod";
import { DB, type Database, type Tx } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { AuditService } from "../identity/audit.service";
import { UndoRegistry } from "../identity/undo";
import { searchWishes, searchWishStatus } from "./analytics.schema";
import { PSEUDONYM_DAYS } from "./analytics.service";

/** Langste zoekwoord dat we bewaren (ADR 0084). */
export const WISH_MAX = 40;
/**
 * Een gemist zoekwoord verschijnt in het admin panel vanaf zoveel verschillende bezoekers. Nu 1, omdat er nog weinig
 * bezoekers zijn; ophogen (bijv. naar 3) als de lijst vol raakt met tikfouten of namen. Niets gaat verloren: lager
 * dan de drempel wordt wel bewaard, alleen niet getoond.
 */
export const MISS_THRESHOLD = 1;

/**
 * Zoekwoord gelijk maken: kleine letters, zonder accenten, één spatie. Null als het geen bruikbaar of
 * mogelijk persoonlijk zoekwoord is: een e-mailadres, een webadres, een telefoon- of ander nummer.
 */
export function normalizeTerm(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const t = value.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase().replace(/[^\p{L}\p{N}' -]+/gu, " ").replace(/\s+/g, " ").trim();
  if (t.length < 2 || t.length > WISH_MAX) return null;
  if (/@|https?|www|\d{4,}/.test(value.toLowerCase()) || /\d{4,}/.test(t.replace(/ /g, ""))) return null;
  if (!/\p{L}/u.test(t)) return null;
  return t;
}

export const WishInput = z.object({
  term: z.string().max(80),
  market: z.string().regex(/^[a-z]{2}-[A-Z]{2}$/),
  kind: z.enum(["miss", "request"]),
  visitorHash: z.string().regex(/^[A-Za-z0-9_-]{16,64}$/),
}).strict();
export type WishInput = z.infer<typeof WishInput>;

export const WishStatusInput = z.object({ term: z.string().min(2).max(WISH_MAX), status: z.enum(["open", "made", "hidden"]) }).strict();

type Status = "open" | "made" | "hidden";

/**
 * Gezocht op de site (ADR 0084): wat bezoekers zochten zonder resultaat en welke platen ze aanvroegen,
 * zodat we weten wat we nog moeten maken.
 */
@Injectable()
export class WishesService implements OnModuleInit {
  constructor(@Inject(DB) private readonly db: Database, private readonly audit: AuditService, private readonly undo: UndoRegistry) {}

  onModuleInit() {
    this.undo.register("analytics.wish.status", {
      permission: "analytics.wishes.manage", label: "Gezocht",
      apply: async (tx: Tx, tenantId: string, _subject: string, before: unknown) => {
        const b = before as { term: string; status: Status };
        await this.write(tx, tenantId, b.term, b.status);
      },
    });
  }

  /** Eén zoekwoord bewaren; dubbel (zelfde dag, woord, markt, soort en bezoek) telt niet opnieuw. False = niet bewaard. */
  async record(tenantId: string, input: WishInput, now = new Date()): Promise<boolean> {
    const term = normalizeTerm(input.term);
    if (!term) return false;
    await withTenant(this.db, tenantId, (tx) => tx.insert(searchWishes)
      .values({ tenantId, day: now.toISOString().slice(0, 10), term, market: input.market, kind: input.kind, visitorHash: input.visitorHash })
      .onConflictDoNothing());
    return true;
  }

  /** Bezoekerscodes na 90 dagen weg; de rijen (en dus de aantallen) blijven. */
  async anonymize(tenantId: string, now = new Date()): Promise<void> {
    const cutoff = new Date(now.getTime() - PSEUDONYM_DAYS * 86_400_000).toISOString().slice(0, 10);
    await withTenant(this.db, tenantId, (tx) => tx.update(searchWishes).set({ visitorHash: null })
      .where(and(eq(searchWishes.tenantId, tenantId), lt(searchWishes.day, cutoff), sql`${searchWishes.visitorHash} is not null`)));
  }

  /**
   * Lijst voor het admin panel: per zoekwoord bezoekers die het misten, aanvragen, markten en de laatste dag.
   * Gemist vanaf MISS_THRESHOLD bezoekers, aanvragen altijd. Verborgen woorden alleen als je erom vraagt.
   */
  async list(tenantId: string, opts: { hidden?: boolean } = {}) {
    const rows = await withTenant(this.db, tenantId, async (tx) => ({
      terms: await tx.select({
        term: searchWishes.term,
        missed: sql<number>`count(*) filter (where ${searchWishes.kind} = 'miss')::int`,
        requested: sql<number>`count(*) filter (where ${searchWishes.kind} = 'request')::int`,
        markets: sql<string[]>`array_agg(distinct ${searchWishes.market} order by ${searchWishes.market})`,
        last: sql<string>`max(${searchWishes.day})::text`,
      }).from(searchWishes).where(eq(searchWishes.tenantId, tenantId)).groupBy(searchWishes.term),
      status: await tx.select({ term: searchWishStatus.term, status: searchWishStatus.status }).from(searchWishStatus).where(eq(searchWishStatus.tenantId, tenantId)),
    }));
    const status = new Map(rows.status.map((s) => [s.term, s.status as Status]));
    return {
      threshold: MISS_THRESHOLD,
      terms: rows.terms
        .map((r) => ({ ...r, status: status.get(r.term) ?? ("open" as Status) }))
        .filter((r) => (r.requested > 0 || r.missed >= MISS_THRESHOLD) && (opts.hidden || r.status !== "hidden"))
        .sort((a, b) => (a.status === "open" ? 0 : 1) - (b.status === "open" ? 0 : 1) || (b.requested * 3 + b.missed) - (a.requested * 3 + a.missed) || b.last.localeCompare(a.last))
        .slice(0, 300),
    };
  }

  async setStatus(tenantId: string, actor: string, term: string, status: Status): Promise<void> {
    const t = normalizeTerm(term);
    if (!t) return;
    await withTenant(this.db, tenantId, async (tx) => {
      const before = (await tx.select({ status: searchWishStatus.status }).from(searchWishStatus)
        .where(and(eq(searchWishStatus.tenantId, tenantId), eq(searchWishStatus.term, t))))[0]?.status ?? "open";
      if (before === status) return;
      await this.write(tx, tenantId, t, status);
      await this.audit.record(tx, tenantId, { actor, action: "analytics.wish.status", subject: t, before: { term: t, status: before }, after: { term: t, status } });
    });
  }

  private async write(tx: Tx, tenantId: string, term: string, status: Status) {
    if (status === "open") {
      await tx.delete(searchWishStatus).where(and(eq(searchWishStatus.tenantId, tenantId), eq(searchWishStatus.term, term)));
      return;
    }
    await tx.insert(searchWishStatus).values({ tenantId, term, status })
      .onConflictDoUpdate({ target: [searchWishStatus.tenantId, searchWishStatus.term], set: { status, updatedAt: new Date() } });
  }
}
