import { Test } from "@nestjs/testing";
import type { NestFastifyApplication } from "@nestjs/platform-fastify";
import { AppModule } from "../src/app.module";
import { fastifyAdapter, hardenApp } from "../src/bootstrap";
import { ADMIN_AUTHENTICATOR, type AdminAuthenticator } from "../src/modules/identity/admin.guard";

export const TENANT = "0192f6a0-0000-7000-8000-000000000001";
export const INGEST_KEY = "test-ingest-key-0123456789abcdef0123456789";

/** Nep-beheerders voor tests. In productie controleert @t-jarpis/auth het Zitadel-token. */
export const fakeAdmins: AdminAuthenticator = {
  async authenticate(header) {
    if (header === "Bearer beheerder") return { subject: "user-beheerder", permissions: ["operations.ratelimit.read", "operations.ratelimit.manage", "analytics.read"] };
    if (header === "Bearer analist") return { subject: "user-analist", permissions: ["analytics.read", "operations.ratelimit.read"] };
    return null;
  },
};

export async function createTestApp() {
  process.env.NODE_ENV = "test";
  delete process.env.DATABASE_URL;
  process.env.TENANT_ID = TENANT;
  process.env.INGEST_KEY = INGEST_KEY;
  process.env.AGGREGATE_INTERVAL_MS = "0";
  const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).overrideProvider(ADMIN_AUTHENTICATOR).useValue(fakeAdmins).compile();
  const app = hardenApp(moduleRef.createNestApplication<NestFastifyApplication>(fastifyAdapter()));
  await app.init();
  const fastify = app.getHttpAdapter().getInstance();
  await fastify.ready();
  return { app, http: fastify };
}
