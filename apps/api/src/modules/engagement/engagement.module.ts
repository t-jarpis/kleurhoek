import { Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { FavoritesController } from "./engagement.controller";
import { EngagementService } from "./engagement.service";

/** Domein Betrokkenheid (ADR 0039): wat een websiteaccount bewaart. Nu: favorieten. */
@Module({ imports: [CatalogModule], controllers: [FavoritesController], providers: [EngagementService], exports: [EngagementService] })
export class EngagementModule {}
