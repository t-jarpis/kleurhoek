import { Module } from "@nestjs/common";
import { DatabaseModule } from "./db/database.module";
import { AnalyticsModule } from "./modules/analytics/analytics.module";
import { HealthController } from "./modules/health/health.controller";
import { IdentityModule } from "./modules/identity/identity.module";
import { OperationsModule } from "./modules/operations/operations.module";
import { OrganizationsModule } from "./modules/organizations/organizations.module";
import { ShopModule } from "./modules/shop/shop.module";
import { StorefrontModule } from "./modules/storefront/storefront.module";

@Module({
  imports: [DatabaseModule, IdentityModule, OperationsModule, OrganizationsModule, ShopModule, StorefrontModule, AnalyticsModule],
  controllers: [HealthController],
})
export class AppModule {}
