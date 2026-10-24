import { Module } from "@nestjs/common";
import { LocalizationModule } from "../localization/localization.module";
import { AdminCollectionsController } from "./admin-collections.controller";
import { CatalogService } from "./catalog.service";

@Module({ imports: [LocalizationModule], controllers: [AdminCollectionsController], providers: [CatalogService], exports: [CatalogService] })
export class CatalogModule {}
