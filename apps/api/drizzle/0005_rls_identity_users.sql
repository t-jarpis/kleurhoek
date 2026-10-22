-- Gebruikers, rollen en koppelingen: alleen zichtbaar binnen de eigen tenant.
GRANT SELECT, INSERT, UPDATE, DELETE ON identity.users TO app_user;
--> statement-breakpoint
ALTER TABLE identity.users ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE identity.users FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON identity.users USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON identity.roles TO app_user;
--> statement-breakpoint
ALTER TABLE identity.roles ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE identity.roles FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON identity.roles USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON identity.user_roles TO app_user;
--> statement-breakpoint
ALTER TABLE identity.user_roles ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE identity.user_roles FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON identity.user_roles USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
