-- Auditlog is alleen-toevoegen: app_user mag niet wijzigen of verwijderen.
GRANT USAGE ON SCHEMA identity TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT ON identity.audit_events TO app_user;
--> statement-breakpoint
ALTER TABLE identity.audit_events ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE identity.audit_events FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON identity.audit_events USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT USAGE ON SCHEMA operations TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON operations.rate_limits TO app_user;
--> statement-breakpoint
ALTER TABLE operations.rate_limits ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE operations.rate_limits FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON operations.rate_limits USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON operations.rate_limit_stats TO app_user;
--> statement-breakpoint
ALTER TABLE operations.rate_limit_stats ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE operations.rate_limit_stats FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON operations.rate_limit_stats USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
