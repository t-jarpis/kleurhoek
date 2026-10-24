import { Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { AdminAnalyticsController, EventIngestController } from "./analytics.controller";
import { AggregationScheduler } from "./aggregation.scheduler";
import { AnalyticsService } from "./analytics.service";
import { GoalsService } from "./goals.service";

@Module({ imports: [CatalogModule], controllers: [EventIngestController, AdminAnalyticsController], providers: [AnalyticsService, AggregationScheduler, GoalsService], exports: [AnalyticsService] })
export class AnalyticsModule {}
