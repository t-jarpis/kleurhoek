CREATE SCHEMA "contact";
--> statement-breakpoint
CREATE SCHEMA "sources";
--> statement-breakpoint
CREATE TABLE "contact"."channels" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"enabled" boolean DEFAULT false NOT NULL,
	"settings" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "contact"."conversations" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"channel" text NOT NULL,
	"topic" text NOT NULL,
	"status" text DEFAULT 'new' NOT NULL,
	"name" text,
	"email" text,
	"phone" text,
	"org" text NOT NULL,
	"market" text NOT NULL,
	"last_message_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_by" text
);
--> statement-breakpoint
CREATE TABLE "contact"."messages" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"conversation_id" uuid NOT NULL,
	"direction" text NOT NULL,
	"body" text NOT NULL,
	"author" text,
	"external_id" text
);
--> statement-breakpoint
CREATE TABLE "sources"."sources" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"theme_slug" text NOT NULL,
	"url" text NOT NULL,
	"basis" text DEFAULT 'link' NOT NULL,
	"license_note" text,
	"license_date" date,
	"status" text DEFAULT 'pending' NOT NULL,
	"health" text DEFAULT 'unknown' NOT NULL,
	"changed" boolean DEFAULT false NOT NULL,
	"http_status" integer,
	"final_url" text,
	"robots_allowed" boolean,
	"page_title" text,
	"check_note" text,
	"content_hash" text,
	"baseline_hash" text,
	"fail_count" integer DEFAULT 0 NOT NULL,
	"last_checked_at" timestamp with time zone,
	"last_ok_at" timestamp with time zone,
	"approved_by" text,
	"approved_at" timestamp with time zone,
	"sort_order" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sources"."themes" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"status" text DEFAULT 'draft' NOT NULL,
	"maker_name" text NOT NULL,
	"maker_url" text NOT NULL,
	"product_slugs" text[] DEFAULT '{}' NOT NULL,
	"sort_order" integer DEFAULT 0 NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "channels_tenant_slug" ON "contact"."channels" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE INDEX "conversations_tenant_status" ON "contact"."conversations" USING btree ("tenant_id","status","last_message_at");--> statement-breakpoint
CREATE INDEX "messages_conversation" ON "contact"."messages" USING btree ("tenant_id","conversation_id","created_at");--> statement-breakpoint
CREATE UNIQUE INDEX "sources_tenant_url" ON "sources"."sources" USING btree ("tenant_id","url");--> statement-breakpoint
CREATE INDEX "sources_tenant_theme" ON "sources"."sources" USING btree ("tenant_id","theme_slug");--> statement-breakpoint
CREATE INDEX "sources_tenant_checked" ON "sources"."sources" USING btree ("tenant_id","status","last_checked_at");--> statement-breakpoint
CREATE UNIQUE INDEX "themes_tenant_slug" ON "sources"."themes" USING btree ("tenant_id","slug");
--> statement-breakpoint
-- Contact en Bronnen: alleen zichtbaar binnen de eigen tenant (zoals 0001_rls).
GRANT USAGE ON SCHEMA contact TO app_user;
--> statement-breakpoint
GRANT USAGE ON SCHEMA sources TO app_user;
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON contact.channels TO app_user;
--> statement-breakpoint
ALTER TABLE contact.channels ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE contact.channels FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON contact.channels USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON contact.conversations TO app_user;
--> statement-breakpoint
ALTER TABLE contact.conversations ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE contact.conversations FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON contact.conversations USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON contact.messages TO app_user;
--> statement-breakpoint
ALTER TABLE contact.messages ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE contact.messages FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON contact.messages USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON sources.sources TO app_user;
--> statement-breakpoint
ALTER TABLE sources.sources ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE sources.sources FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON sources.sources USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON sources.themes TO app_user;
--> statement-breakpoint
ALTER TABLE sources.themes ENABLE ROW LEVEL SECURITY;
--> statement-breakpoint
ALTER TABLE sources.themes FORCE ROW LEVEL SECURITY;
--> statement-breakpoint
CREATE POLICY tenant_isolation ON sources.themes USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
