import { Controller, Delete, Get, HttpCode, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { OrganizationsService } from "../organizations/organizations.service";
import { IdentityService } from "./identity.service";
import { MemberGuard } from "./member.guard";

/** Het eigen account van een websitegebruiker. Wordt bij de eerste aanroep aangemaakt (just in time). */
@Controller("v1/me")
@UseGuards(MemberGuard)
export class MeController {
  constructor(private readonly identity: IdentityService, private readonly orgs: OrganizationsService) {}

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
    await this.identity.deleteSelf(req.member!.userId);
  }
}
