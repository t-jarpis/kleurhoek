import { Global, Module } from "@nestjs/common";
import { AdminOrganizationsController, OrganizationsController } from "./organizations.controller";
import { OrganizationsService } from "./organizations.service";

/** Domein Organisaties (ADR 0017): Kleurhoek en whitelabel-partners, met huisstijl, domein en aanbod. */
@Global()
@Module({ controllers: [AdminOrganizationsController, OrganizationsController], providers: [OrganizationsService], exports: [OrganizationsService] })
export class OrganizationsModule {}
