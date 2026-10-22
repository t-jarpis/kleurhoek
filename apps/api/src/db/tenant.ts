import { sql } from "drizzle-orm";
import type { Database, Tx } from "./database";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * Voert werk uit binnen één transactie als rol app_user, met app.tenant_id gezet.
 * Row-level security zorgt dat alleen rijen van deze tenant zichtbaar en schrijfbaar zijn.
 */
export async function withTenant<T>(db: Database, tenantId: string, work: (tx: Tx) => Promise<T>): Promise<T> {
  if (!UUID.test(tenantId)) throw new Error("Ongeldige tenant");
  return db.transaction(async (tx) => {
    await tx.execute(sql`select set_config('app.tenant_id', ${tenantId}, true)`);
    await tx.execute(sql`set local role app_user`);
    return work(tx as Tx);
  });
}
