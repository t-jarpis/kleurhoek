CREATE TABLE "analytics"."goals" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"metric" text NOT NULL,
	"start_month" text NOT NULL,
	"milestones" jsonb NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "goals_tenant_metric" ON "analytics"."goals" USING btree ("tenant_id","metric");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.goals TO app_user;
--> statement-breakpoint
ALTER TABLE analytics.goals ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE analytics.goals FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.goals USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
