import { Test } from "@nestjs/testing";
import type { NestFastifyApplication } from "@nestjs/platform-fastify";
import { AppModule } from "../src/app.module";
import { fastifyAdapter, hardenApp } from "../src/bootstrap";
import { ADMIN_AUTHENTICATOR, type AdminAuthenticator } from "../src/modules/identity/admin.guard";
import { MAIL_TRANSPORT, MemoryTransport } from "../src/modules/messaging/mailer";

export const TENANT = "0192f6a0-0000-7000-8000-000000000001";
export const INGEST_KEY = "test-ingest-key-0123456789abcdef0123456789";
export const ADMIN_ORG = "org-beheer";
export const SITE_ORG = "org-kleurhoek";
export const AUDIENCE = "project-kleurhoek";

/** Nep-beheerders voor tests die niet over inloggen gaan. */
export const fakeAdmins: AdminAuthenticator = {
  async authenticate({ authorization }) {
    if (authorization === "Bearer beheerder") return { userId: "0192f6a0-0000-7000-8000-0000000000b1", subject: "user-beheerder", permissions: ["operations.ratelimit.read", "operations.ratelimit.manage", "operations.access.read", "operations.access.manage", "organizations.read", "organizations.manage", "analytics.read", "analytics.goals.manage", "shop.read", "shop.manage", "contact.read", "contact.manage", "sources.read", "sources.manage", "seo.read", "seo.manage", "mail.read", "mail.manage"] };
    if (authorization === "Bearer analist") return { userId: "0192f6a0-0000-7000-8000-0000000000a1", subject: "user-analist", permissions: ["analytics.read", "operations.ratelimit.read", "releases.read"] };
    return null;
  },
};

const OIDC_KEYS = ["OIDC_ISSUER", "OIDC_AUDIENCE", "ADMIN_ORG_ID", "SITE_ORG_ID", "ADMIN_BOOTSTRAP_SUBJECTS", "ADMIN_DEV_TOKEN"] as const;

/**
 * Start de API in het geheugen. Zonder `oidc` met nep-beheerders; met `oidc` precies zoals in
 * productie, tegen een nep-Zitadel uit @t-jarpis/auth/testing.
 */
export async function createTestApp(options: { oidc?: { issuer: string; bootstrap?: string[] }; mail?: MemoryTransport } = {}) {
  process.env.NODE_ENV = "test";
  delete process.env.DATABASE_URL;
  process.env.TENANT_ID = TENANT;
  process.env.INGEST_KEY = INGEST_KEY;
  process.env.AGGREGATE_INTERVAL_MS = "0";
  process.env.MAIL_INTERVAL_MS = "0";
  process.env.SITE_URL = "https://www.kleurhoek.test";
  for (const key of OIDC_KEYS) delete process.env[key];
  if (options.oidc) {
    process.env.OIDC_ISSUER = options.oidc.issuer;
    process.env.OIDC_AUDIENCE = AUDIENCE;
    process.env.ADMIN_ORG_ID = ADMIN_ORG;
    process.env.SITE_ORG_ID = SITE_ORG;
    process.env.ADMIN_BOOTSTRAP_SUBJECTS = (options.oidc.bootstrap ?? []).join(",");
  }
  let builder = Test.createTestingModule({ imports: [AppModule] });
  if (!options.oidc) builder = builder.overrideProvider(ADMIN_AUTHENTICATOR).useValue(fakeAdmins);
  // Mail gaat in tests nooit naar buiten: een transport in het geheugen (ADR 0037).
  const mail = options.mail ?? new MemoryTransport();
  builder = builder.overrideProvider(MAIL_TRANSPORT).useValue(mail);
  const moduleRef = await builder.compile();
  const app = hardenApp(moduleRef.createNestApplication<NestFastifyApplication>(fastifyAdapter()));
  await app.init();
  const fastify = app.getHttpAdapter().getInstance();
  await fastify.ready();
  return { app, http: fastify, mail };
}
