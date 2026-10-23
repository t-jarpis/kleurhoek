import { NestFactory } from "@nestjs/core";
import type { NestFastifyApplication } from "@nestjs/platform-fastify";
import { AppModule } from "./app.module";
import { fastifyAdapter, hardenApp } from "./bootstrap";
import { loadEnv } from "./config/env";
import { describeDbError } from "./db/database.module";

async function main() {
  const env = loadEnv();
  const app = hardenApp(await NestFactory.create<NestFastifyApplication>(AppModule, fastifyAdapter(), { logger: ["error", "warn", "log"] }));
  // Netjes stoppen bij een nieuwe versie: tellers wegschrijven en de database sluiten.
  app.enableShutdownHooks();
  await app.listen({ port: env.PORT, host: "0.0.0.0" });
}
main().catch((e: unknown) => {
  console.error(e);
  // Kort en als laatste regel: Scaleway toont alleen het einde van de uitvoer als foutmelding van de container.
  console.error(`Opstarten mislukt: ${describeDbError(e)}`);
  process.exit(1);
});
