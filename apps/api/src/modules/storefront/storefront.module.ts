import { Module } from "@nestjs/common";
import { AvailabilityModule } from "../availability/availability.module";
import { CatalogModule } from "../catalog/catalog.module";
import { LocalizationModule } from "../localization/localization.module";
import { StorefrontController } from "./storefront.controller";
import { StorefrontService } from "./storefront.service";

@Module({ imports: [CatalogModule, LocalizationModule, AvailabilityModule], controllers: [StorefrontController], providers: [StorefrontService] })
export class StorefrontModule {}
