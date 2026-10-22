import { CanActivate, ExecutionContext, Inject, Injectable, SetMetadata, UnauthorizedException, ForbiddenException } from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import type { FastifyRequest } from "fastify";

export interface AdminPrincipal { subject: string; permissions: string[] }

/**
 * Controleert wie de beheerder is. Tot Zitadel gekoppeld is (via @t-jarpis/auth) weigert de
 * standaardimplementatie alles: zero trust, dus nooit standaard open.
 */
export interface AdminAuthenticator { authenticate(authorization: string | undefined): Promise<AdminPrincipal | null> }
export const ADMIN_AUTHENTICATOR = Symbol("ADMIN_AUTHENTICATOR");

export class DenyAllAuthenticator implements AdminAuthenticator {
  async authenticate(): Promise<AdminPrincipal | null> { return null; }
}

/** Alleen in development: één vaste token met alle rechten, om het admin panel lokaal te kunnen gebruiken. */
export class DevTokenAuthenticator implements AdminAuthenticator {
  constructor(private readonly token: string) {}
  async authenticate(header: string | undefined): Promise<AdminPrincipal | null> {
    if (header !== `Bearer ${this.token}`) return null;
    return { subject: "dev-beheerder", permissions: ["operations.ratelimit.read", "operations.ratelimit.manage", "analytics.read"] };
  }
}

export const PERMISSION = "permission";
/** Vereiste permissie voor een admin-endpoint, bijvoorbeeld `operations.ratelimit.manage`. */
export const RequirePermission = (permission: string) => SetMetadata(PERMISSION, permission);

declare module "fastify" { interface FastifyRequest { admin?: AdminPrincipal } }

@Injectable()
export class AdminGuard implements CanActivate {
  constructor(@Inject(ADMIN_AUTHENTICATOR) private readonly auth: AdminAuthenticator, private readonly reflector: Reflector) {}

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<FastifyRequest>();
    const principal = await this.auth.authenticate(req.headers.authorization);
    if (!principal) throw new UnauthorizedException();
    const needed = this.reflector.getAllAndOverride<string | undefined>(PERMISSION, [ctx.getHandler(), ctx.getClass()]);
    if (!needed || !principal.permissions.includes(needed)) throw new ForbiddenException();
    req.admin = principal;
    return true;
  }
}
