CREATE SCHEMA "together";
--> statement-breakpoint
CREATE TABLE "together"."room_ops" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"seq" bigint GENERATED ALWAYS AS IDENTITY (sequence name "together"."room_ops_seq_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1),
	"room_id" uuid NOT NULL,
	"client" text NOT NULL,
	"body" jsonb NOT NULL
);
--> statement-breakpoint
CREATE TABLE "together"."room_presence" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"room_id" uuid NOT NULL,
	"client" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "together"."rooms" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"code" text NOT NULL,
	"market" text NOT NULL,
	"plate_slug" text NOT NULL,
	"plate_version" integer NOT NULL,
	"active_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "together"."room_ops" ADD CONSTRAINT "room_ops_room_id_rooms_id_fk" FOREIGN KEY ("room_id") REFERENCES "together"."rooms"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "together"."room_presence" ADD CONSTRAINT "room_presence_room_id_rooms_id_fk" FOREIGN KEY ("room_id") REFERENCES "together"."rooms"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "room_ops_room_seq" ON "together"."room_ops" USING btree ("room_id","seq");--> statement-breakpoint
CREATE UNIQUE INDEX "room_presence_client" ON "together"."room_presence" USING btree ("room_id","client");--> statement-breakpoint
CREATE UNIQUE INDEX "rooms_code" ON "together"."rooms" USING btree ("tenant_id","code");--> statement-breakpoint
CREATE INDEX "rooms_active" ON "together"."rooms" USING btree ("active_at");--> statement-breakpoint
GRANT USAGE ON SCHEMA together TO app_user;--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON together.rooms, together.room_ops, together.room_presence TO app_user;--> statement-breakpoint
ALTER TABLE together.rooms ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE together.rooms FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON together.rooms USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
ALTER TABLE together.room_ops ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE together.room_ops FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON together.room_ops USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);--> statement-breakpoint
ALTER TABLE together.room_presence ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE together.room_presence FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON together.room_presence USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
