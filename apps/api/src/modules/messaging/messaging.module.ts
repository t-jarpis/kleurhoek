import { Module } from "@nestjs/common";
import { CatalogModule } from "../catalog/catalog.module";
import { LocalizationModule } from "../localization/localization.module";
import { StorefrontModule } from "../storefront/storefront.module";
import { CampaignsService } from "./campaigns.service";
import { MAIL_TRANSPORT, SmtpTransport } from "./mailer";
import { AdminMailController, MailController, MeMailController } from "./messaging.controller";
import { MessagingScheduler } from "./messaging.scheduler";
import { OutboxService } from "./outbox.service";
import { SubscribersService } from "./subscribers.service";
import { TemplatesService } from "./templates.service";
import { WorkflowsService } from "./workflows.service";

/** Domein Berichten (ADR 0037): abonnees, templates, workflows, campagnes en de wachtrij naar SMTP. */
@Module({
  imports: [CatalogModule, LocalizationModule, StorefrontModule],
  controllers: [MailController, MeMailController, AdminMailController],
  providers: [{ provide: MAIL_TRANSPORT, useClass: SmtpTransport }, SubscribersService, TemplatesService, OutboxService, WorkflowsService, CampaignsService, MessagingScheduler],
  exports: [SubscribersService],
})
export class MessagingModule {}
