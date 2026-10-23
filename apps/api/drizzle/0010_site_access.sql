CREATE TABLE "operations"."site_access" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"enabled" boolean DEFAULT false NOT NULL,
	"entries" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "site_access_tenant" ON "operations"."site_access" USING btree ("tenant_id");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON operations.site_access TO app_user;
--> statement-breakpoint
ALTER TABLE operations.site_access ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE operations.site_access FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON operations.site_access USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
