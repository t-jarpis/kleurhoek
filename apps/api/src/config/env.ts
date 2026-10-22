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
});

export type Env = z.infer<typeof schema>;

export function loadEnv(source: NodeJS.ProcessEnv = process.env): Env {
  const env = schema.parse(source);
  if (env.NODE_ENV === "production") {
    if (!env.DATABASE_URL) throw new Error("DATABASE_URL is verplicht in productie");
    if (env.INGEST_KEY.startsWith("dev-only")) throw new Error("INGEST_KEY moet in productie gezet zijn");
  }
  return env;
}

export const ENV = Symbol("ENV");
