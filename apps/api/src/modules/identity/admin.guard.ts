import { CanActivate, ExecutionContext, ForbiddenException, Inject, Injectable, SetMetadata, UnauthorizedException } from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import type { FastifyRequest } from "fastify";
import { ALL_PERMISSIONS, type Permission } from "./permissions";

export interface AdminPrincipal { userId: string; subject: string; permissions: Permission[] }

/** Wat een authenticator van het verzoek te zien krijgt. Bewust weinig: geen toegang tot de hele request. */
export interface AuthContext { authorization: string | undefined; country: string | undefined }

/**
 * Controleert wie de beheerder is. Zero trust: zonder geldig token van de beheerorganisatie, met een
 * actieve gebruiker en een rol, komt niemand binnen. De standaardimplementatie weigert alles.
 */
export interface AdminAuthenticator { authenticate(ctx: AuthContext): Promise<AdminPrincipal | null> }
export const ADMIN_AUTHENTICATOR = Symbol("ADMIN_AUTHENTICATOR");

export class DenyAllAuthenticator implements AdminAuthenticator {
  async authenticate(): Promise<AdminPrincipal | null> { return null; }
}

/** Alleen in development zonder Zitadel: één vaste token met alle rechten. Verboden in productie (zie env.ts). */
export class DevTokenAuthenticator implements AdminAuthenticator {
  constructor(private readonly token: string) {}
  async authenticate({ authorization }: AuthContext): Promise<AdminPrincipal | null> {
    if (authorization !== `Bearer ${this.token}`) return null;
    return { userId: "00000000-0000-7000-8000-00000000dev0", subject: "dev-beheerder", permissions: ALL_PERMISSIONS };
  }
}

export function authContext(req: FastifyRequest): AuthContext {
  const cf = req.headers["cf-ipcountry"];
  const country = typeof cf === "string" && /^[A-Z]{2}$/.test(cf) && cf !== "XX" && cf !== "T1" ? cf : undefined;
  return { authorization: req.headers.authorization, country };
}

export const PERMISSION = "permission";
/** Vereiste permissie voor een admin-endpoint, bijvoorbeeld `operations.ratelimit.manage`. */
export const RequirePermission = (permission: Permission) => SetMetadata(PERMISSION, permission);
/** Elke ingelogde beheerder, ongeacht rechten. Alleen voor "wie ben ik"-achtige endpoints. */
export const RequireAdmin = () => SetMetadata(PERMISSION, ANY_ADMIN);
const ANY_ADMIN = "*";

declare module "fastify" { interface FastifyRequest { admin?: AdminPrincipal } }

@Injectable()
export class AdminGuard implements CanActivate {
  constructor(@Inject(ADMIN_AUTHENTICATOR) private readonly auth: AdminAuthenticator, private readonly reflector: Reflector) {}

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<FastifyRequest>();
    const principal = await this.auth.authenticate(authContext(req));
    if (!principal) throw new UnauthorizedException();
    const needed = this.reflector.getAllAndOverride<Permission | typeof ANY_ADMIN | undefined>(PERMISSION, [ctx.getHandler(), ctx.getClass()]);
    // Deny by default: een endpoint zonder permissie is voor niemand.
    if (!needed || (needed !== ANY_ADMIN && !principal.permissions.includes(needed))) throw new ForbiddenException();
    req.admin = principal;
    return true;
  }
}
