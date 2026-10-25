CREATE SCHEMA "engagement";
--> statement-breakpoint
CREATE TABLE "engagement"."favorites" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"user_id" uuid NOT NULL,
	"plate_slug" text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX "favorites_user_plate" ON "engagement"."favorites" USING btree ("tenant_id","user_id","plate_slug");--> statement-breakpoint
GRANT USAGE ON SCHEMA engagement TO app_user;--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON engagement.favorites TO app_user;--> statement-breakpoint
ALTER TABLE engagement.favorites ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE engagement.favorites FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON engagement.favorites USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
