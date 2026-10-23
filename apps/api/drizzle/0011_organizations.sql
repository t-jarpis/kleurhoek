CREATE SCHEMA "organizations";
--> statement-breakpoint
CREATE TABLE "organizations"."logos" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"organization_id" uuid NOT NULL,
	"content_type" text NOT NULL,
	"sha256" text NOT NULL,
	"data" "bytea" NOT NULL
);
--> statement-breakpoint
CREATE TABLE "organizations"."organizations" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"kind" text NOT NULL,
	"active" boolean DEFAULT true NOT NULL,
	"is_default" boolean DEFAULT false NOT NULL,
	"hosts" text[] DEFAULT '{}' NOT NULL,
	"brand" jsonb NOT NULL,
	"offer" jsonb NOT NULL,
	"features" jsonb NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "logos_organization" ON "organizations"."logos" USING btree ("tenant_id","organization_id");--> statement-breakpoint
CREATE UNIQUE INDEX "organizations_tenant_slug" ON "organizations"."organizations" USING btree ("tenant_id","slug");--> statement-breakpoint
GRANT USAGE ON SCHEMA organizations TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON organizations.organizations TO app_user;
--> statement-breakpoint
ALTER TABLE organizations.organizations ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE organizations.organizations FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON organizations.organizations USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON organizations.logos TO app_user;
--> statement-breakpoint
ALTER TABLE organizations.logos ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE organizations.logos FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON organizations.logos USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
