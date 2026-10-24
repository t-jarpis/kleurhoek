CREATE TABLE "operations"."releases" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"sha" text NOT NULL,
	"previous_sha" text,
	"kind" text NOT NULL,
	"notes" jsonb NOT NULL,
	"started_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE INDEX "releases_tenant_started" ON "operations"."releases" USING btree ("tenant_id","started_at");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON operations.releases TO app_user;
--> statement-breakpoint
ALTER TABLE operations.releases ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE operations.releases FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON operations.releases USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
