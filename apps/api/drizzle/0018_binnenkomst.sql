CREATE TABLE "analytics"."daily_sources" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"org" text NOT NULL,
	"entry_domain" text NOT NULL,
	"referrer" text NOT NULL,
	"landings" integer DEFAULT 0 NOT NULL,
	"visitors" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
ALTER TABLE "analytics"."events" ADD COLUMN "entry_domain" text;--> statement-breakpoint
ALTER TABLE "analytics"."events" ADD COLUMN "referrer" text;--> statement-breakpoint
CREATE UNIQUE INDEX "daily_sources_unique" ON "analytics"."daily_sources" USING btree ("tenant_id","day","org","entry_domain","referrer");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.daily_sources TO app_user;--> statement-breakpoint
ALTER TABLE analytics.daily_sources ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE analytics.daily_sources FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.daily_sources USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
