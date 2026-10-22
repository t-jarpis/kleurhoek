-- Nieuwe tabellen van Werkjes en Winkel: alleen zichtbaar binnen de eigen tenant.
GRANT USAGE ON SCHEMA shop TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.materials TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.materials ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.materials FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.materials USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.plate_materials TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.plate_materials ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.plate_materials FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.plate_materials USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.daily_product_clicks TO app_user;
--> statement-breakpoint
ALTER TABLE analytics.daily_product_clicks ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE analytics.daily_product_clicks FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.daily_product_clicks USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.partners TO app_user;
--> statement-breakpoint
ALTER TABLE shop.partners ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE shop.partners FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON shop.partners USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.products TO app_user;
--> statement-breakpoint
ALTER TABLE shop.products ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE shop.products FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON shop.products USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.material_products TO app_user;
--> statement-breakpoint
ALTER TABLE shop.material_products ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE shop.material_products FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON shop.material_products USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
