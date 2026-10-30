CREATE SCHEMA "social";
--> statement-breakpoint
CREATE TABLE "social"."channels" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"kind" text NOT NULL,
	"account" text,
	"external_id" text,
	"token" text,
	"settings" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"enabled" integer DEFAULT 1 NOT NULL,
	"connected_at" timestamp with time zone,
	"error" text
);
--> statement-breakpoint
CREATE TABLE "social"."posts" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"channel" text NOT NULL,
	"status" text DEFAULT 'voorstel' NOT NULL,
	"key" text NOT NULL,
	"source" text NOT NULL,
	"market" text NOT NULL,
	"plate_slug" text,
	"title" text NOT NULL,
	"body" text NOT NULL,
	"link" text NOT NULL,
	"image" text NOT NULL,
	"board" text,
	"scheduled_at" timestamp with time zone NOT NULL,
	"decided_at" timestamp with time zone,
	"decided_by" text,
	"published_at" timestamp with time zone,
	"external_url" text,
	"attempts" integer DEFAULT 0 NOT NULL,
	"error" text
);
--> statement-breakpoint
CREATE TABLE "social"."settings" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"value" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"digest_sent_on" text,
	"generated_on" text
);
--> statement-breakpoint
CREATE UNIQUE INDEX "channels_kind" ON "social"."channels" USING btree ("tenant_id","kind");--> statement-breakpoint
CREATE UNIQUE INDEX "posts_key" ON "social"."posts" USING btree ("tenant_id","channel","key");--> statement-breakpoint
CREATE UNIQUE INDEX "settings_tenant" ON "social"."settings" USING btree ("tenant_id");--> statement-breakpoint
GRANT USAGE ON SCHEMA social TO app_user;--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON social.channels, social.posts, social.settings TO app_user;--> statement-breakpoint
ALTER TABLE social.channels ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE social.channels FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON social.channels USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
ALTER TABLE social.posts ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE social.posts FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON social.posts USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
ALTER TABLE social.settings ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE social.settings FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON social.settings USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
