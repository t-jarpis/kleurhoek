import path from "node:path";
import { PGlite } from "@electric-sql/pglite";
import type { ExtractTablesWithRelations } from "drizzle-orm";
import { drizzle as drizzlePglite } from "drizzle-orm/pglite";
import { migrate as migratePglite } from "drizzle-orm/pglite/migrator";
import { drizzle as drizzlePg } from "drizzle-orm/node-postgres";
import { migrate as migratePg } from "drizzle-orm/node-postgres/migrator";
import type { PgDatabase, PgQueryResultHKT, PgTransaction } from "drizzle-orm/pg-core";
import { Pool } from "pg";
import * as schema from "./schema";

export type Schema = typeof schema;
export type Database = PgDatabase<PgQueryResultHKT, Schema>;
export type Tx = PgTransaction<PgQueryResultHKT, Schema, ExtractTablesWithRelations<Schema>>;

export const DB = Symbol("DB");
const migrationsFolder = path.join(__dirname, "..", "..", "drizzle");

export interface DatabaseHandle {
  db: Database;
  migrate(): Promise<void>;
  close(): Promise<void>;
}

/** Productie en staging: PostgreSQL via een connection pool. */
export function connectPostgres(url: string): DatabaseHandle {
  const pool = new Pool({ connectionString: url, max: 10, idleTimeoutMillis: 30_000 });
  const db = drizzlePg(pool, { schema });
  return {
    db: db as unknown as Database,
    migrate: () => migratePg(db, { migrationsFolder }),
    close: () => pool.end(),
  };
}

/** Lokaal en in tests: PostgreSQL in het geheugen via PGlite, zonder server. */
export function connectInMemory(): DatabaseHandle {
  const client = new PGlite();
  const db = drizzlePglite(client, { schema });
  return {
    db: db as unknown as Database,
    migrate: () => migratePglite(db, { migrationsFolder }),
    close: () => client.close(),
  };
}
