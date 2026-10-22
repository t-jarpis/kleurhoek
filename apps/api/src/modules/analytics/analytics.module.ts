import { Module } from "@nestjs/common";
import { AdminAnalyticsController, EventIngestController } from "./analytics.controller";
import { AnalyticsService } from "./analytics.service";

@Module({ controllers: [EventIngestController, AdminAnalyticsController], providers: [AnalyticsService], exports: [AnalyticsService] })
export class AnalyticsModule {}
