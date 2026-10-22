import { loadEnv } from "../config/env";
import { connectPostgres } from "./database";

/** CLI: draait alle migraties tegen DATABASE_URL. Gebruikt in de deploy-pijplijn vóór de nieuwe versie. */
async function main() {
  const env = loadEnv();
  if (!env.DATABASE_URL) throw new Error("DATABASE_URL ontbreekt");
  const handle = connectPostgres(env.DATABASE_URL);
  await handle.migrate();
  await handle.close();
  console.warn("Migraties klaar");
}
void main().catch((e) => { console.error(e); process.exit(1); });
