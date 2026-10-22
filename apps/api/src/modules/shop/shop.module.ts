import { Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { LocalizationModule } from "../localization/localization.module";
import { AdminShopController } from "./admin-shop.controller";
import { ShopService } from "./shop.service";

/** Domein Winkel. Fase 1: doorverwijzen naar partners (affiliate). Zie ADR 0011. */
@Module({ imports: [CatalogModule, LocalizationModule], controllers: [AdminShopController], providers: [ShopService], exports: [ShopService] })
export class ShopModule {}
