import { createHmac } from "node:crypto";
import { isLocalUrl } from "@t-jarpis/auth";
import { z } from "zod";

const flag = z.enum(["true", "false", "1", "0", ""]).default("false").transform((v) => v === "true" || v === "1");

const schema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(3001),
  /** Leeg = een PGlite-database in het geheugen met seed-data (alleen lokaal). */
  DATABASE_URL: z.string().url().optional(),
  /** CA-certificaat (PEM) van de database; gezet = TLS met controle tegen deze CA. */
  DATABASE_CA: z.string().optional(),
  /** Migraties draaien bij het opstarten (Scaleway: er is geen aparte job in het privénetwerk). */
  MIGRATE_ON_START: flag,
  /** De catalogus vullen bij het opstarten (idempotent). Aan in dev, uit in productie. */
  SEED_ON_START: flag,
  /** Subdomein per organisatie, met {slug}: "{slug}-dev.kleurhoek.nl" (dev) of "{slug}.kleurhoek.nl" (prod). Leeg = alleen vaste hosts. */
  ORG_HOST_PATTERN: z.string().regex(/^\{slug\}[a-z0-9.-]+$/).optional(),
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
  /** Commit van deze build (Dockerfile, ARG BUILD_SHA). Leeg lokaal: dan geen releases vastleggen. */
  BUILD_SHA: z.union([z.literal(""), z.string().regex(/^[0-9a-f]{7,40}$/)]).optional().transform((v) => v || undefined),
  /** Commits van de build voor de releasenotes (gemaakt in de Deploy-workflow). */
  RELEASE_LOG_PATH: z.string().default("release-log.json"),
  AGGREGATE_INTERVAL_MS: z.coerce.number().int().min(0).default(600_000),
  // ---------- Mail (ADR 0037) ----------
  /** Adres van de website, voor links in mails (bevestigen, afmelden, platen). */
  SITE_URL: z.string().url().default("http://localhost:3000"),
  /** Afzender, bijvoorbeeld "Kleurhoek <hallo@kleurhoek.nl>". */
  MAIL_FROM: z.string().min(3).default("Kleurhoek <hallo@kleurhoek.localhost>"),
  /** SMTP voor nieuwsbrief en automatische mails: smtp(s)://gebruiker:wachtwoord@host:poort. Leeg = versturen staat uit. */
  MAIL_SMTP_URL: z.string().regex(/^smtps?:\/\//).optional(),
  /** SMTP voor bevestigingsmails (transactioneel). Leeg = dezelfde als MAIL_SMTP_URL. */
  MAIL_TRANSACTIONAL_SMTP_URL: z.string().regex(/^smtps?:\/\//).optional(),
  /** Geheim voor afmeldlinks (HMAC). Leeg = afgeleid van INGEST_KEY (dan werkt een nieuwe uitrol ook vóór Terraform). */
  MAIL_SECRET: z.string().min(32).optional(),
  /** Hoeveel mails per minuut hooguit. */
  MAIL_RATE_PER_MINUTE: z.coerce.number().int().min(1).max(10_000).default(120),
  /** Hoe vaak de wachtrij en workflows worden verwerkt. 0 = uit (tests). */
  MAIL_INTERVAL_MS: z.coerce.number().int().min(0).default(20_000),
});

export type Env = Omit<z.infer<typeof schema>, "MAIL_SECRET"> & { MAIL_SECRET: string };

/** Inloggen staat aan als uitgever, publiek en beheerorganisatie bekend zijn. */
export function oidcEnabled(env: Env): env is Env & { OIDC_ISSUER: string; OIDC_AUDIENCE: string; ADMIN_ORG_ID: string } {
  return Boolean(env.OIDC_ISSUER && env.OIDC_AUDIENCE && env.ADMIN_ORG_ID);
}

export function loadEnv(source: NodeJS.ProcessEnv = process.env): Env {
  const parsed = schema.parse(source);
  const env = { ...parsed, MAIL_SECRET: parsed.MAIL_SECRET ?? createHmac("sha256", parsed.INGEST_KEY).update("kleurhoek-mail").digest("hex") };
  if (env.NODE_ENV === "production") {
    if (!env.DATABASE_URL) throw new Error("DATABASE_URL is verplicht in productie");
    if (env.INGEST_KEY.startsWith("dev-only")) throw new Error("INGEST_KEY moet in productie gezet zijn");
    if (env.ADMIN_DEV_TOKEN) throw new Error("ADMIN_DEV_TOKEN is niet toegestaan in productie");
    for (const key of ["OIDC_ISSUER", "OIDC_AUDIENCE", "ADMIN_ORG_ID", "SITE_ORG_ID"] as const) {
      if (!env[key]) throw new Error(`${key} is verplicht in productie`);
    }
    // Http alleen als Zitadel op deze machine draait (docker compose).
    if (!env.OIDC_ISSUER?.startsWith("https://") && !isLocalUrl(env.OIDC_ISSUER ?? "")) throw new Error("OIDC_ISSUER moet https zijn in productie");
  }
  return env;
}

export const ENV = Symbol("ENV");
