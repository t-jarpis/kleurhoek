import { randomInt } from "node:crypto";
import { Inject, Injectable } from "@nestjs/common";
import { and, asc, count, eq, gt, lt, ne, sql } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { roomOps, roomPresence, rooms } from "./together.schema";

/** Letters die je niet met een cijfer of andere letter verwart (geen I en O). */
export const CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ";
export const CODE = /^[A-HJ-NP-Z]{4}$/;
/** Een kamer stopt als er zo lang niemand meer in is. Zolang iemand kleurt, blijft hij bestaan. */
export const IDLE_MS = 30 * 60_000;
/** Wie de laatste tijd heeft gevraagd wat er nieuw is, telt als aanwezig. */
const PRESENT_MS = 30_000;
export const MAX_OPS = 5000;

export interface Room { id: string; code: string; market: string; slug: string; version: number }

/**
 * Samen kleuren (ADR 0060). Een eigen domein met een eigen schema; kent de platen niet, alleen hun naam en versie.
 * Wat er gekleurd wordt, staat als een lijst handelingen in de kamer; elk apparaat bouwt daar zelf de plaat uit op.
 */
@Injectable()
export class TogetherService {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env) {}
  private get tenant() { return this.env.TENANT_ID; }
  private tx<T>(fn: Parameters<typeof withTenant<T>>[2]) { return withTenant(this.db, this.tenant, fn); }

  async create(market: string, slug: string, version: number): Promise<Room> {
    for (let attempt = 0; attempt < 20; attempt++) {
      const code = Array.from({ length: 4 }, () => CODE_LETTERS[randomInt(CODE_LETTERS.length)]).join("");
      const [row] = await this.tx((tx) => tx.insert(rooms).values({ tenantId: this.tenant, code, market, plateSlug: slug, plateVersion: version })
        .onConflictDoNothing().returning({ id: rooms.id }));
      if (row) return { id: row.id, code, market, slug, version };
    }
    throw new Error("Geen vrije code gevonden");
  }

  async find(code: string): Promise<Room | null> {
    const since = new Date(Date.now() - IDLE_MS);
    const [r] = await this.tx((tx) => tx.select().from(rooms).where(and(eq(rooms.tenantId, this.tenant), eq(rooms.code, code), gt(rooms.activeAt, since))));
    return r ? { id: r.id, code: r.code, market: r.market, slug: r.plateSlug, version: r.plateVersion } : null;
  }

  /** Handelingen toevoegen. Geeft false als de kamer vol is. */
  async add(room: Room, client: string, ops: unknown[]): Promise<boolean> {
    return this.tx(async (tx) => {
      const [{ n }] = await tx.select({ n: count() }).from(roomOps).where(eq(roomOps.roomId, room.id)) as [{ n: number }];
      if (Number(n) + ops.length > MAX_OPS) return false;
      if (ops.length) await tx.insert(roomOps).values(ops.map((body) => ({ tenantId: this.tenant, roomId: room.id, client, body })));
      await tx.update(rooms).set({ activeAt: new Date() }).where(eq(rooms.id, room.id));
      return true;
    });
  }

  /** Wat er nieuw is na `after`, en hoeveel anderen er nu zijn. Telt de vrager meteen als aanwezig. */
  async since(room: Room, client: string, after: number) {
    return this.tx(async (tx) => {
      const now = new Date();
      await tx.insert(roomPresence).values({ tenantId: this.tenant, roomId: room.id, client }).onConflictDoUpdate({ target: [roomPresence.roomId, roomPresence.client], set: { updatedAt: now } });
      await tx.update(rooms).set({ activeAt: now }).where(eq(rooms.id, room.id));
      const ops = await tx.select({ seq: roomOps.seq, client: roomOps.client, body: roomOps.body }).from(roomOps)
        .where(and(eq(roomOps.roomId, room.id), gt(roomOps.seq, after))).orderBy(asc(roomOps.seq)).limit(500);
      const [{ n }] = await tx.select({ n: count() }).from(roomPresence)
        .where(and(eq(roomPresence.roomId, room.id), ne(roomPresence.client, client), gt(roomPresence.updatedAt, new Date(Date.now() - PRESENT_MS)))) as [{ n: number }];
      return { ops: ops.map((o) => ({ seq: o.seq, client: o.client, op: o.body })), others: Number(n), last: ops.at(-1)?.seq ?? after };
    });
  }

  /** Kamers waar al een half uur niemand meer is, met alles erin. */
  async cleanup(now = new Date()) {
    const res = await this.tx((tx) => tx.delete(rooms).where(and(eq(rooms.tenantId, this.tenant), lt(rooms.activeAt, new Date(now.getTime() - IDLE_MS)))).returning({ id: rooms.id }));
    return res.length;
  }

  /** Voor tests: een kamer laten verouderen. */
  async age(code: string, ms: number) {
    await this.tx((tx) => tx.update(rooms).set({ activeAt: sql`active_at - (${ms} || ' milliseconds')::interval` }).where(eq(rooms.code, code)));
  }
}
