import "reflect-metadata";
import { FastifyAdapter, type NestFastifyApplication } from "@nestjs/platform-fastify";
import type { INestApplicationContext } from "@nestjs/common";

/** Beveiligingsheaders en grenzen die voor elke API-response gelden. */
export function hardenApp(app: NestFastifyApplication) {
  const fastify = app.getHttpAdapter().getInstance();
  fastify.addHook("onSend", async (_req, reply, payload) => {
    reply.header("X-Content-Type-Options", "nosniff");
    reply.header("Referrer-Policy", "no-referrer");
    reply.header("X-Frame-Options", "DENY");
    reply.header("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload");
    if (!reply.hasHeader("Content-Security-Policy")) reply.header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'");
    if (!reply.hasHeader("Cache-Control")) reply.header("Cache-Control", "no-store");
    reply.removeHeader("X-Powered-By");
    return payload;
  });
  app.enableShutdownHooks();
  return app;
}

export function fastifyAdapter() {
  return new FastifyAdapter({ bodyLimit: 64 * 1024, trustProxy: false, logger: false });
}

export type App = NestFastifyApplication & INestApplicationContext;
