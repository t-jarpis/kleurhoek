import { loadEnv } from "../config/env";
import { connectPostgres } from "./database";

/** CLI: draait alle migraties tegen DATABASE_URL. Voor handmatig gebruik; in Scaleway migreert de API bij het opstarten (MIGRATE_ON_START). */
async function main() {
  const env = loadEnv();
  if (!env.DATABASE_URL) throw new Error("DATABASE_URL ontbreekt");
  const handle = connectPostgres(env.DATABASE_URL, { ca: env.DATABASE_CA });
  await handle.migrate();
  await handle.close();
  console.warn("Migraties klaar");
}
void main().catch((e) => { console.error(e); process.exit(1); });
