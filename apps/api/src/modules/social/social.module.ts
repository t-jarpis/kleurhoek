import { Module } from "@nestjs/common";
import { MessagingModule } from "../messaging/messaging.module";
import { StorefrontModule } from "../storefront/storefront.module";
import { SocialController } from "./social.controller";
import { SocialScheduler } from "./social.scheduler";
import { SocialService } from "./social.service";

/** Domein Social (ADR 0063): voorstellen voor social media, goedkeuren en plaatsen op Pinterest, Facebook en Instagram. */
@Module({ imports: [StorefrontModule, MessagingModule], controllers: [SocialController], providers: [SocialService, SocialScheduler], exports: [SocialService] })
export class SocialModule {}
