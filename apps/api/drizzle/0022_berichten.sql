CREATE SCHEMA "messaging";
--> statement-breakpoint
CREATE TABLE "messaging"."campaigns" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"name" text NOT NULL,
	"template" text NOT NULL,
	"audience" jsonb NOT NULL,
	"context" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"status" text DEFAULT 'draft' NOT NULL,
	"scheduled_at" timestamp with time zone,
	"sent_at" timestamp with time zone,
	"recipients" integer DEFAULT 0 NOT NULL,
	"created_by" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "messaging"."deliveries" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"subscriber_id" uuid NOT NULL,
	"source" text NOT NULL,
	"template" text NOT NULL,
	"context" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"transactional" boolean DEFAULT false NOT NULL,
	"status" text DEFAULT 'queued' NOT NULL,
	"attempts" integer DEFAULT 0 NOT NULL,
	"error" text,
	"sent_at" timestamp with time zone
);
--> statement-breakpoint
CREATE TABLE "messaging"."daily_stats" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"metric" text NOT NULL,
	"value" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "messaging"."subscribers" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"email" text NOT NULL,
	"market" text NOT NULL,
	"organization" text DEFAULT 'kleurhoek' NOT NULL,
	"topics" text[] DEFAULT '{}' NOT NULL,
	"status" text DEFAULT 'pending' NOT NULL,
	"user_id" uuid,
	"confirm_token_hash" text,
	"confirm_sent_at" timestamp with time zone,
	"consent_at" timestamp with time zone NOT NULL,
	"confirmed_at" timestamp with time zone
);
--> statement-breakpoint
CREATE TABLE "messaging"."templates" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"kind" text NOT NULL,
	"subject" jsonb NOT NULL,
	"preheader" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"blocks" jsonb NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "messaging"."workflow_runs" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"workflow_slug" text NOT NULL,
	"subscriber_id" uuid NOT NULL,
	"occasion" text NOT NULL,
	"step" integer DEFAULT 0 NOT NULL,
	"due_at" timestamp with time zone NOT NULL,
	"status" text DEFAULT 'waiting' NOT NULL,
	"context" jsonb DEFAULT '{}'::jsonb NOT NULL
);
--> statement-breakpoint
CREATE TABLE "messaging"."workflows" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"enabled" boolean DEFAULT false NOT NULL,
	"trigger" jsonb NOT NULL,
	"steps" jsonb NOT NULL,
	"cursor" timestamp with time zone,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
ALTER TABLE "messaging"."deliveries" ADD CONSTRAINT "deliveries_subscriber_id_subscribers_id_fk" FOREIGN KEY ("subscriber_id") REFERENCES "messaging"."subscribers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "messaging"."workflow_runs" ADD CONSTRAINT "workflow_runs_subscriber_id_subscribers_id_fk" FOREIGN KEY ("subscriber_id") REFERENCES "messaging"."subscribers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "deliveries_once" ON "messaging"."deliveries" USING btree ("tenant_id","source","subscriber_id");--> statement-breakpoint
CREATE INDEX "deliveries_queue" ON "messaging"."deliveries" USING btree ("tenant_id","status","created_at");--> statement-breakpoint
CREATE UNIQUE INDEX "daily_stats_day_metric" ON "messaging"."daily_stats" USING btree ("tenant_id","day","metric");--> statement-breakpoint
CREATE UNIQUE INDEX "subscribers_email" ON "messaging"."subscribers" USING btree ("tenant_id","organization","email");--> statement-breakpoint
CREATE INDEX "subscribers_status" ON "messaging"."subscribers" USING btree ("tenant_id","status");--> statement-breakpoint
CREATE UNIQUE INDEX "templates_slug" ON "messaging"."templates" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "workflow_runs_once" ON "messaging"."workflow_runs" USING btree ("tenant_id","workflow_slug","subscriber_id","occasion");--> statement-breakpoint
CREATE INDEX "workflow_runs_due" ON "messaging"."workflow_runs" USING btree ("tenant_id","status","due_at");--> statement-breakpoint
CREATE UNIQUE INDEX "workflows_slug" ON "messaging"."workflows" USING btree ("tenant_id","slug");
--> statement-breakpoint
GRANT USAGE ON SCHEMA messaging TO app_user;--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.subscribers TO app_user;--> statement-breakpoint
ALTER TABLE messaging.subscribers ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.subscribers FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.subscribers USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.templates TO app_user;--> statement-breakpoint
ALTER TABLE messaging.templates ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.templates FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.templates USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.workflows TO app_user;--> statement-breakpoint
ALTER TABLE messaging.workflows ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.workflows FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.workflows USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.workflow_runs TO app_user;--> statement-breakpoint
ALTER TABLE messaging.workflow_runs ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.workflow_runs FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.workflow_runs USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.campaigns TO app_user;--> statement-breakpoint
ALTER TABLE messaging.campaigns ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.campaigns FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.campaigns USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.deliveries TO app_user;--> statement-breakpoint
ALTER TABLE messaging.deliveries ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.deliveries FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.deliveries USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.daily_stats TO app_user;--> statement-breakpoint
ALTER TABLE messaging.daily_stats ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.daily_stats FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.daily_stats USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
