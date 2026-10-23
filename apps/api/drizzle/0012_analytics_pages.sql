CREATE TABLE "analytics"."daily_pages" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"org" text NOT NULL,
	"page" text NOT NULL,
	"market" text NOT NULL,
	"device" text NOT NULL,
	"views" integer DEFAULT 0 NOT NULL,
	"visitors" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "analytics"."daily_visitors" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"org" text NOT NULL,
	"visitors" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
ALTER TABLE "analytics"."events" ADD COLUMN "page" text;--> statement-breakpoint
ALTER TABLE "analytics"."events" ADD COLUMN "org" text;--> statement-breakpoint
CREATE UNIQUE INDEX "daily_pages_unique" ON "analytics"."daily_pages" USING btree ("tenant_id","day","org","page","market","device");--> statement-breakpoint
CREATE UNIQUE INDEX "daily_visitors_unique" ON "analytics"."daily_visitors" USING btree ("tenant_id","day","org");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.daily_pages TO app_user;
--> statement-breakpoint
ALTER TABLE analytics.daily_pages ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE analytics.daily_pages FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.daily_pages USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.daily_visitors TO app_user;
--> statement-breakpoint
ALTER TABLE analytics.daily_visitors ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE analytics.daily_visitors FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.daily_visitors USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
