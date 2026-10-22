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
  /** Zitadel-uitgever, bijvoorbeeld https://login.kleurhoek.nl. Leeg = inloggen uit (alleen lokaal). */
  OIDC_ISSUER: z.string().url().optional(),
  /** Project-ID van Kleurhoek in Zitadel: het publiek (`aud`) van access tokens. */
  OIDC_AUDIENCE: z.string().min(1).optional(),
  /** Organisatie van de beheerders (Org Beheer). Alleen zij komen in het admin panel. */
  ADMIN_ORG_ID: z.string().min(1).optional(),
  /** Organisatie van de websitegebruikers. */
  SITE_ORG_ID: z.string().min(1).optional(),
  /** Zitadel-ID's die bij hun eerste login platformbeheerder worden. Kommagescheiden; daarna via het admin panel. */
  ADMIN_BOOTSTRAP_SUBJECTS: z.string().default("").transform((v) => v.split(",").map((s) => s.trim()).filter(Boolean)),
  /** Hoe vaak de dagtotalen worden bijgewerkt. 0 = uit (tests). */
  AGGREGATE_INTERVAL_MS: z.coerce.number().int().min(0).default(600_000),
});

export type Env = z.infer<typeof schema>;

/** Inloggen staat aan als uitgever, publiek en beheerorganisatie bekend zijn. */
export function oidcEnabled(env: Env): env is Env & { OIDC_ISSUER: string; OIDC_AUDIENCE: string; ADMIN_ORG_ID: string } {
  return Boolean(env.OIDC_ISSUER && env.OIDC_AUDIENCE && env.ADMIN_ORG_ID);
}

export function loadEnv(source: NodeJS.ProcessEnv = process.env): Env {
  const env = schema.parse(source);
  if (env.NODE_ENV === "production") {
    if (!env.DATABASE_URL) throw new Error("DATABASE_URL is verplicht in productie");
    if (env.INGEST_KEY.startsWith("dev-only")) throw new Error("INGEST_KEY moet in productie gezet zijn");
    if (env.ADMIN_DEV_TOKEN) throw new Error("ADMIN_DEV_TOKEN is niet toegestaan in productie");
    for (const key of ["OIDC_ISSUER", "OIDC_AUDIENCE", "ADMIN_ORG_ID", "SITE_ORG_ID"] as const) {
      if (!env[key]) throw new Error(`${key} is verplicht in productie`);
    }
    if (!env.OIDC_ISSUER?.startsWith("https://")) throw new Error("OIDC_ISSUER moet https zijn in productie");
  }
  return env;
}

export const ENV = Symbol("ENV");
