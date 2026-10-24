import { Global, Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { LocalizationModule } from "../localization/localization.module";
import { AdminOrganizationsController, MeOrganizationsController, OrganizationsController } from "./organizations.controller";
import { OrganizationsService } from "./organizations.service";

/** Domein Organisaties (ADR 0017): Kleurhoek en whitelabel-partners, met huisstijl, domein en aanbod. */
@Global()
@Module({ imports: [LocalizationModule, CatalogModule], controllers: [AdminOrganizationsController, OrganizationsController, MeOrganizationsController], providers: [OrganizationsService], exports: [OrganizationsService] })
export class OrganizationsModule {}
