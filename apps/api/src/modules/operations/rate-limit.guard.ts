import { CanActivate, ExecutionContext, HttpException, HttpStatus, Injectable, SetMetadata } from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import type { FastifyReply, FastifyRequest } from "fastify";
import { RateLimitService } from "./rate-limit.service";

export const RATE_LIMIT_RULE = "rateLimitRule";
/** Koppelt een endpoint aan een rate-limitregel. Zonder decorator geldt `api-default`. */
export const RateLimit = (rule: string) => SetMetadata(RATE_LIMIT_RULE, rule);
export const SkipRateLimit = () => SetMetadata(RATE_LIMIT_RULE, false);

/**
 * Het IP-adres van de bezoeker. De origin accepteert alleen verkeer van Cloudflare (authenticated
 * origin pulls), dus CF-Connecting-IP is betrouwbaar. Zonder Cloudflare (lokaal) het socket-adres.
 */
export function clientIp(req: FastifyRequest): string {
  const cf = req.headers["cf-connecting-ip"];
  return (typeof cf === "string" && cf) || req.ip;
}

@Injectable()
export class RateLimitGuard implements CanActivate {
  constructor(private readonly limits: RateLimitService, private readonly reflector: Reflector) {}

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    if (ctx.getType() !== "http") return true;
    const rule = this.reflector.getAllAndOverride<string | false | undefined>(RATE_LIMIT_RULE, [ctx.getHandler(), ctx.getClass()]);
    if (rule === false) return true;
    const req = ctx.switchToHttp().getRequest<FastifyRequest>();
    const reply = ctx.switchToHttp().getResponse<FastifyReply>();
    const slug = rule ?? "api-default";
    const identity = slug === "events-ingest" ? "worker" : req.admin?.subject ?? clientIp(req);
    const d = await this.limits.check(slug, identity);
    if (!d) return true;
    reply.header("RateLimit-Policy", `${d.limit};w=${d.windowSeconds}`);
    reply.header("RateLimit", `limit=${d.limit}, remaining=${d.remaining}, reset=${d.resetSeconds}`);
    if (!d.allowed) {
      reply.header("Retry-After", String(d.resetSeconds));
      throw new HttpException({ statusCode: 429, error: "Too Many Requests", message: `Te veel verzoeken. Probeer het over ${d.resetSeconds} seconden opnieuw.` }, HttpStatus.TOO_MANY_REQUESTS);
    }
    return true;
  }
}
