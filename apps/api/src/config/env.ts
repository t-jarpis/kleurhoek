import { z } from "zod";

const schema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(3001),
  /** Leeg = een PGlite-database in het geheugen met seed-data (alleen lokaal). */
  DATABASE_URL: z.string().url().optional(),
  /** De tenant van deze site. Kleurhoek heeft er nu één. */
  TENANT_ID: z.string().uuid().default("0192f6a0-0000-7000-8000-000000000001"),
  /** Gedeelde sleutel waarmee de Cloudflare Worker events aanlevert. */
  INGEST_KEY: z.string().min(32).default("dev-only-ingest-key-change-me-0000000000"),
  /** Alleen lokaal: een vaste beheerderstoken tot Zitadel gekoppeld is. Verboden in productie. */
  ADMIN_DEV_TOKEN: z.string().min(32).optional(),
  /** Hoe vaak de dagtotalen worden bijgewerkt. 0 = uit (tests). */
  AGGREGATE_INTERVAL_MS: z.coerce.number().int().min(0).default(600_000),
});

export type Env = z.infer<typeof schema>;

export function loadEnv(source: NodeJS.ProcessEnv = process.env): Env {
  const env = schema.parse(source);
  if (env.NODE_ENV === "production") {
    if (!env.DATABASE_URL) throw new Error("DATABASE_URL is verplicht in productie");
    if (env.INGEST_KEY.startsWith("dev-only")) throw new Error("INGEST_KEY moet in productie gezet zijn");
    if (env.ADMIN_DEV_TOKEN) throw new Error("ADMIN_DEV_TOKEN is niet toegestaan in productie");
  }
  return env;
}

export const ENV = Symbol("ENV");
