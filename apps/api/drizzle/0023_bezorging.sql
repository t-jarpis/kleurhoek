CREATE TABLE "messaging"."delivery_events" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"type" text NOT NULL,
	"provider" text NOT NULL,
	"email_hash" text NOT NULL,
	"domain" text NOT NULL,
	"delivery_id" uuid,
	"source" text,
	"template" text,
	"reason" text,
	"occurred_at" timestamp with time zone NOT NULL
);
--> statement-breakpoint
CREATE TABLE "messaging"."suppressions" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"email_hash" text NOT NULL,
	"domain" text NOT NULL,
	"reason" text NOT NULL,
	"detail" text,
	"expires_at" timestamp with time zone,
	"created_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
ALTER TABLE "messaging"."deliveries" ADD COLUMN "message_id" text;--> statement-breakpoint
CREATE INDEX "delivery_events_time" ON "messaging"."delivery_events" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE INDEX "delivery_events_email" ON "messaging"."delivery_events" USING btree ("tenant_id","email_hash","occurred_at");--> statement-breakpoint
CREATE UNIQUE INDEX "suppressions_email" ON "messaging"."suppressions" USING btree ("tenant_id","email_hash");--> statement-breakpoint
CREATE INDEX "deliveries_message_id" ON "messaging"."deliveries" USING btree ("tenant_id","message_id");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.delivery_events TO app_user;--> statement-breakpoint
ALTER TABLE messaging.delivery_events ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.delivery_events FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.delivery_events USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON messaging.suppressions TO app_user;--> statement-breakpoint
ALTER TABLE messaging.suppressions ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE messaging.suppressions FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON messaging.suppressions USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
