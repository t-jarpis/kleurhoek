import { loadEnv } from "../config/env";
import { connectPostgres } from "./database";
import { seed } from "./seed";

/** CLI: vult een lege database met de catalogus. Idempotent; voor handmatig gebruik; in dev vult de API hem bij het opstarten (SEED_ON_START). */
async function main() {
  const env = loadEnv();
  if (!env.DATABASE_URL) throw new Error("DATABASE_URL ontbreekt");
  const handle = connectPostgres(env.DATABASE_URL, { ca: env.DATABASE_CA });
  const result = await seed(handle.db, env.TENANT_ID);
  await handle.close();
  console.warn(result.plates ? `Catalogus bijgewerkt: ${result.plates} nieuwe platen` : "Catalogus is al bij; niets nieuws");
}
void main().catch((e) => { console.error(e); process.exit(1); });
