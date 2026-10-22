import { NestFactory } from "@nestjs/core";
import type { NestFastifyApplication } from "@nestjs/platform-fastify";
import { AppModule } from "./app.module";
import { fastifyAdapter, hardenApp } from "./bootstrap";
import { loadEnv } from "./config/env";

async function main() {
  const env = loadEnv();
  const app = hardenApp(await NestFactory.create<NestFastifyApplication>(AppModule, fastifyAdapter(), { logger: ["error", "warn", "log"] }));
  await app.listen({ port: env.PORT, host: "0.0.0.0" });
}
void main();
