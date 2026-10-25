import { Controller, Delete, Get, HttpCode, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { ModuleRef } from "@nestjs/core";
import { EngagementService } from "../engagement/engagement.service";
import { SubscribersService } from "../messaging/subscribers.service";
import { OrganizationsService } from "../organizations/organizations.service";
import { IdentityService } from "./identity.service";
import { MemberGuard } from "./member.guard";

/** Het eigen account van een websitegebruiker. Wordt bij de eerste aanroep aangemaakt (just in time). */
@Controller("v1/me")
@UseGuards(MemberGuard)
export class MeController {
  constructor(private readonly identity: IdentityService, private readonly orgs: OrganizationsService, private readonly modules: ModuleRef) {}

  @Get()
  async me(@Req() req: FastifyRequest) {
    const user = await this.identity.getUser(req.member!.userId);
    return { id: user!.id, displayName: user!.displayName, email: user!.email, locale: user!.locale, createdAt: user!.createdAt };
  }

  /** Account verwijderen. Bij Zitadel blijft het login-account bestaan; dat beheert de gebruiker daar zelf. */
  @Delete()
  @HttpCode(204)
  async remove(@Req() req: FastifyRequest) {
    await this.orgs.forgetUser(req.member!.userId);
    // Ook een mailabonnement via het account (domein Berichten, ADR 0037).
    await this.modules.get(SubscribersService, { strict: false }).forgetUser(req.member!.userId);
    // En de favorieten (domein Betrokkenheid, ADR 0039).
    await this.modules.get(EngagementService, { strict: false }).forgetUser(req.member!.userId);
    await this.identity.deleteSelf(req.member!.userId);
  }
}
