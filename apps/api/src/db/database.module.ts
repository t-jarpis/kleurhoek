import { Global, Inject, Module, type OnApplicationShutdown } from "@nestjs/common";
import { ENV, loadEnv, type Env } from "../config/env";
import { connectInMemory, connectPostgres, DB, type DatabaseHandle } from "./database";
import { seed } from "./seed";

const HANDLE = Symbol("DB_HANDLE");

@Global()
@Module({
  providers: [
    { provide: ENV, useFactory: () => loadEnv() },
    {
      provide: HANDLE,
      inject: [ENV],
      useFactory: async (env: Env): Promise<DatabaseHandle> => {
        if (env.DATABASE_URL) {
          const handle = connectPostgres(env.DATABASE_URL, { ca: env.DATABASE_CA });
          if (env.MIGRATE_ON_START || env.SEED_ON_START) {
            // Meerdere instances kunnen tegelijk starten; het slot laat ze na elkaar migreren.
            await handle.exclusive(async () => {
              if (env.MIGRATE_ON_START) await handle.migrate();
              if (env.SEED_ON_START) await seed(handle.db, env.TENANT_ID);
            });
          }
          return handle;
        }
        // Lokaal zonder database: in het geheugen, gemigreerd en gevuld met de catalogus.
        const handle = connectInMemory();
        await handle.migrate();
        await seed(handle.db, env.TENANT_ID);
        return handle;
      },
    },
    { provide: DB, inject: [HANDLE], useFactory: (h: DatabaseHandle) => h.db },
  ],
  exports: [ENV, DB, HANDLE],
})
export class DatabaseModule implements OnApplicationShutdown {
  constructor(@Inject(HANDLE) private readonly handle: DatabaseHandle) {}
  async onApplicationShutdown() { await this.handle.close(); }
}
export { HANDLE as DB_HANDLE };

/** Eén regel met de echte PostgreSQL-fout (Drizzle verpakt die in `cause`). */
export function describeDbError(e: unknown): string {
  const err = e as { message?: string; cause?: { message?: string; code?: string; detail?: string; hint?: string } };
  const pg = err?.cause ?? {};
  const parts = [pg.message ?? err?.message ?? String(e)];
  if (pg.code) parts.push(`code ${pg.code}`);
  if (pg.detail) parts.push(`detail: ${pg.detail}`);
  if (pg.hint) parts.push(`hint: ${pg.hint}`);
  const query = /Failed query: ([\s\S]{0,160})/.exec(err?.message ?? "")?.[1]?.replace(/\s+/g, " ");
  if (query) parts.push(`query: ${query}`);
  return parts.join(" | ");
}
