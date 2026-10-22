CREATE SCHEMA "identity";
--> statement-breakpoint
CREATE SCHEMA "operations";
--> statement-breakpoint
CREATE TABLE "identity"."audit_events" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"actor" text NOT NULL,
	"action" text NOT NULL,
	"subject" text NOT NULL,
	"before" jsonb,
	"after" jsonb,
	"occurred_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "operations"."rate_limit_stats" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"rule_slug" text NOT NULL,
	"allowed" integer DEFAULT 0 NOT NULL,
	"blocked" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "operations"."rate_limits" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"description" text NOT NULL,
	"limit" integer NOT NULL,
	"window_seconds" integer NOT NULL,
	"key_by" text NOT NULL,
	"enabled" boolean DEFAULT true NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE INDEX "audit_events_tenant_time" ON "identity"."audit_events" USING btree ("tenant_id","occurred_at");--> statement-breakpoint
CREATE UNIQUE INDEX "rate_limit_stats_unique" ON "operations"."rate_limit_stats" USING btree ("tenant_id","day","rule_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "rate_limits_tenant_slug" ON "operations"."rate_limits" USING btree ("tenant_id","slug");