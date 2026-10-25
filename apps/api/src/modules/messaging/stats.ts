import { sql } from "drizzle-orm";
import type { Tx } from "../../db/database";
import { uuidv7 } from "../../shared/uuid";
import { mailStats } from "./messaging.schema";

/** Teller voor vandaag ophogen (aanmeldingen, afmeldingen, verstuurd). Zonder persoonsgegevens. */
export async function bump(tx: Tx, tenantId: string, metric: string, n = 1, now = new Date()) {
  if (n === 0) return;
  await tx.insert(mailStats).values({ id: uuidv7(), tenantId, day: now.toISOString().slice(0, 10), metric, value: n })
    .onConflictDoUpdate({ target: [mailStats.tenantId, mailStats.day, mailStats.metric], set: { value: sql`${mailStats.value} + ${n}`, updatedAt: new Date() } });
}
