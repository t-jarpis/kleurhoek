import { Module } from "@nestjs/common";
import { AdminAnalyticsController, EventIngestController } from "./analytics.controller";
import { AggregationScheduler } from "./aggregation.scheduler";
import { AnalyticsService } from "./analytics.service";

@Module({ controllers: [EventIngestController, AdminAnalyticsController], providers: [AnalyticsService, AggregationScheduler], exports: [AnalyticsService] })
export class AnalyticsModule {}
