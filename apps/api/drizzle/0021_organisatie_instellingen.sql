CREATE TABLE "catalog"."collections" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"names" jsonb NOT NULL,
	"descriptions" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"plates" text[] DEFAULT '{}' NOT NULL,
	"sort_order" integer DEFAULT 0 NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "organizations"."managers" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"organization_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"created_by" text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "collections_tenant_slug" ON "catalog"."collections" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "managers_org_user" ON "organizations"."managers" USING btree ("tenant_id","organization_id","user_id");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON catalog.collections TO app_user;--> statement-breakpoint
ALTER TABLE catalog.collections ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE catalog.collections FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON catalog.collections USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON organizations.managers TO app_user;--> statement-breakpoint
ALTER TABLE organizations.managers ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE organizations.managers FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON organizations.managers USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
