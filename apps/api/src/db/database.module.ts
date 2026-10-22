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
        if (env.DATABASE_URL) return connectPostgres(env.DATABASE_URL);
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
