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
  /** Voert `fn` uit terwijl deze instance een databasebreed slot heeft (andere instances wachten). */
  exclusive<T>(fn: () => Promise<T>): Promise<T>;
  close(): Promise<void>;
}

export interface PostgresOptions {
  /**
   * CA-certificaat (PEM) van de database. Gezet = TLS met controle van de certificaatketen tegen deze CA.
   * De hostnaam wordt niet gecontroleerd: we verbinden via een privé-IP, en de CA hoort alleen bij
   * deze ene database-instance.
   */
  ca?: string;
}

/** Vast getal voor pg_advisory_lock: migraties en seed bij het opstarten. */
const STARTUP_LOCK = 4_242_001;

/** Productie en staging: PostgreSQL via een connection pool. */
export function connectPostgres(url: string, options: PostgresOptions = {}): DatabaseHandle {
  const ssl = options.ca ? { ca: options.ca, checkServerIdentity: () => undefined } : undefined;
  const pool = new Pool({ connectionString: url, ssl, max: 10, idleTimeoutMillis: 30_000 });
  const db = drizzlePg(pool, { schema });
  return {
    db: db as unknown as Database,
    migrate: () => migratePg(db, { migrationsFolder }),
    async exclusive(fn) {
      const client = await pool.connect();
      try {
        await client.query("select pg_advisory_lock($1)", [STARTUP_LOCK]);
        try {
          return await fn();
        } finally {
          await client.query("select pg_advisory_unlock($1)", [STARTUP_LOCK]);
        }
      } finally {
        client.release();
      }
    },
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
    exclusive: (fn) => fn(),
    close: () => client.close(),
  };
}
