-- Zero trust in de database: de app draait als rol app_user en ziet alleen rijen van de eigen tenant.
-- De tenant komt uit app.tenant_id, gezet per transactie (zie src/db/tenant.ts).
DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN CREATE ROLE app_user NOLOGIN; END IF; END $$;
--> statement-breakpoint
GRANT USAGE ON SCHEMA catalog TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.categories TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.categories ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.categories FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.categories USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.ages TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.ages ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.ages FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.ages USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.continents TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.continents ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.continents FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.continents USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.plates TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.plates ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.plates FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.plates USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.plate_versions TO app_user;
--> statement-breakpoint
ALTER TABLE catalog.plate_versions ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE catalog.plate_versions FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.plate_versions USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT USAGE ON SCHEMA localization TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON localization.markets TO app_user;
--> statement-breakpoint
ALTER TABLE localization.markets ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE localization.markets FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON localization.markets USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON localization.translations TO app_user;
--> statement-breakpoint
ALTER TABLE localization.translations ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE localization.translations FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON localization.translations USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT USAGE ON SCHEMA availability TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON availability.plate_rules TO app_user;
--> statement-breakpoint
ALTER TABLE availability.plate_rules ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE availability.plate_rules FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON availability.plate_rules USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON availability.holidays TO app_user;
--> statement-breakpoint
ALTER TABLE availability.holidays ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE availability.holidays FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON availability.holidays USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON availability.holiday_dates TO app_user;
--> statement-breakpoint
ALTER TABLE availability.holiday_dates ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE availability.holiday_dates FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON availability.holiday_dates USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON availability.seasons TO app_user;
--> statement-breakpoint
ALTER TABLE availability.seasons ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE availability.seasons FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON availability.seasons USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT USAGE ON SCHEMA analytics TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.events TO app_user;
--> statement-breakpoint
ALTER TABLE analytics.events ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE analytics.events FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.events USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.daily_totals TO app_user;
--> statement-breakpoint
ALTER TABLE analytics.daily_totals ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE analytics.daily_totals FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.daily_totals USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
