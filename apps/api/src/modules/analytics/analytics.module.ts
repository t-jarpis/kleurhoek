import { Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { AdminAnalyticsController, EventIngestController, WishIngestController } from "./analytics.controller";
import { AggregationScheduler } from "./aggregation.scheduler";
import { AnalyticsService } from "./analytics.service";
import { GoalsService } from "./goals.service";
import { SearchService } from "./search.service";
import { WishesService } from "./wishes.service";

@Module({ imports: [CatalogModule], controllers: [EventIngestController, WishIngestController, AdminAnalyticsController], providers: [AnalyticsService, AggregationScheduler, GoalsService, SearchService, WishesService], exports: [AnalyticsService] })
export class AnalyticsModule {}
