CREATE TABLE "operations"."capacity_daily" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"app" text NOT NULL,
	"cpu_avg" real,
	"cpu_p95" real,
	"mem_avg" real,
	"mem_p95" real,
	"instances_max" integer
);
--> statement-breakpoint
CREATE TABLE "operations"."speed_samples" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"at" timestamp with time zone NOT NULL,
	"path" text NOT NULL,
	"ms" integer NOT NULL,
	"status" integer NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "capacity_daily_unique" ON "operations"."capacity_daily" USING btree ("tenant_id","day","app");--> statement-breakpoint
CREATE INDEX "speed_samples_tenant_at" ON "operations"."speed_samples" USING btree ("tenant_id","at");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON operations.capacity_daily, operations.speed_samples TO app_user;--> statement-breakpoint
ALTER TABLE operations.capacity_daily ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE operations.capacity_daily FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON operations.capacity_daily USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
ALTER TABLE operations.speed_samples ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE operations.speed_samples FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON operations.speed_samples USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
