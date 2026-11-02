import { Controller, Delete, Get, HttpCode, Req, UseGuards } from "@nestjs/common";
import type { FastifyRequest } from "fastify";
import { DomainEvents } from "../../shared/events";
import { IdentityService } from "./identity.service";
import { MemberGuard } from "./member.guard";

/** Het eigen account van een websitegebruiker. Wordt bij de eerste aanroep aangemaakt (just in time). */
@Controller("v1/me")
@UseGuards(MemberGuard)
export class MeController {
  constructor(private readonly identity: IdentityService, private readonly events: DomainEvents) {}

  @Get()
  async me(@Req() req: FastifyRequest) {
    const user = await this.identity.getUser(req.member!.userId);
    return { id: user!.id, displayName: user!.displayName, email: user!.email, locale: user!.locale, createdAt: user!.createdAt };
  }

  /** Account verwijderen. Bij Zitadel blijft het login-account bestaan; dat beheert de gebruiker daar zelf. */
  @Delete()
  @HttpCode(204)
  async remove(@Req() req: FastifyRequest) {
    // Elk domein ruimt zijn gegevens op (organisaties, mail, favorieten); mislukt er één, dan blijft het account
    // bestaan en kan de gebruiker het opnieuw proberen (ADR 0066).
    await this.events.emit("identity.account.deleted", { userId: req.member!.userId }, { strict: true });
    await this.identity.deleteSelf(req.member!.userId);
  }
}
