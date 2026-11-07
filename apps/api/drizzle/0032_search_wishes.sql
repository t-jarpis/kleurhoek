CREATE TABLE "analytics"."search_wish_status" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"term" text NOT NULL,
	"status" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "analytics"."search_wishes" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"term" text NOT NULL,
	"market" text NOT NULL,
	"kind" text NOT NULL,
	"visitor_hash" text
);
--> statement-breakpoint
CREATE UNIQUE INDEX "search_wish_status_term" ON "analytics"."search_wish_status" USING btree ("tenant_id","term");--> statement-breakpoint
CREATE UNIQUE INDEX "search_wishes_unique" ON "analytics"."search_wishes" USING btree ("tenant_id","day","term","market","kind","visitor_hash");--> statement-breakpoint
CREATE INDEX "search_wishes_term" ON "analytics"."search_wishes" USING btree ("tenant_id","term");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON analytics.search_wishes, analytics.search_wish_status TO app_user;--> statement-breakpoint
ALTER TABLE analytics.search_wishes ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE analytics.search_wishes FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.search_wishes USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
ALTER TABLE analytics.search_wish_status ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE analytics.search_wish_status FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON analytics.search_wish_status USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
