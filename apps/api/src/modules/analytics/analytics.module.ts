import { Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { AdminAnalyticsController, EventIngestController } from "./analytics.controller";
import { AggregationScheduler } from "./aggregation.scheduler";
import { AnalyticsService } from "./analytics.service";
import { GoalsService } from "./goals.service";
import { SearchService } from "./search.service";

@Module({ imports: [CatalogModule], controllers: [EventIngestController, AdminAnalyticsController], providers: [AnalyticsService, AggregationScheduler, GoalsService, SearchService], exports: [AnalyticsService] })
export class AnalyticsModule {}
