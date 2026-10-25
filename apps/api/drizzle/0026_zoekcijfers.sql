CREATE TABLE "analytics"."search_stats" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"engine" text NOT NULL,
	"site" text NOT NULL,
	"kind" text NOT NULL,
	"key" text NOT NULL,
	"clicks" integer DEFAULT 0 NOT NULL,
	"impressions" integer DEFAULT 0 NOT NULL,
	"position" real
);
--> statement-breakpoint
CREATE TABLE "analytics"."search_sync" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"engine" text NOT NULL,
	"site" text NOT NULL,
	"ok" boolean NOT NULL,
	"message" text,
	"last_day" date,
	"run_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "search_stats_unique" ON "analytics"."search_stats" USING btree ("tenant_id","day","engine","site","kind","key");--> statement-breakpoint
CREATE INDEX "search_stats_day" ON "analytics"."search_stats" USING btree ("tenant_id","day");--> statement-breakpoint
CREATE UNIQUE INDEX "search_sync_unique" ON "analytics"."search_sync" USING btree ("tenant_id","engine","site");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.search_stats TO app_user;--> statement-breakpoint
ALTER TABLE analytics.search_stats ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE analytics.search_stats FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.search_stats USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.search_sync TO app_user;--> statement-breakpoint
ALTER TABLE analytics.search_sync ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE analytics.search_sync FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.search_sync USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
