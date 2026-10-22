CREATE SCHEMA "catalog";
--> statement-breakpoint
CREATE SCHEMA "localization";
--> statement-breakpoint
CREATE SCHEMA "availability";
--> statement-breakpoint
CREATE SCHEMA "analytics";
--> statement-breakpoint
CREATE TABLE "catalog"."ages" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"sort_order" integer NOT NULL,
	"level" integer NOT NULL,
	"stroke_width" real NOT NULL
);
--> statement-breakpoint
CREATE TABLE "catalog"."categories" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"sort_order" integer NOT NULL,
	"color" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "catalog"."continents" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"sort_order" integer NOT NULL,
	"color" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "catalog"."plate_versions" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"plate_id" uuid NOT NULL,
	"version" integer NOT NULL,
	"svg" text NOT NULL,
	"region_count" integer NOT NULL,
	"color_by_number" jsonb NOT NULL,
	"created_by" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "catalog"."plates" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"category_slug" text NOT NULL,
	"age_slug" text NOT NULL,
	"continent_slug" text,
	"depicted_country" text,
	"holiday_slug" text,
	"status" text DEFAULT 'draft' NOT NULL,
	"sort_order" integer DEFAULT 0 NOT NULL,
	"current_version_id" uuid
);
--> statement-breakpoint
CREATE TABLE "localization"."markets" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"code" text NOT NULL,
	"country" text NOT NULL,
	"language" text NOT NULL,
	"status" text DEFAULT 'draft' NOT NULL,
	"paper_size" text DEFAULT 'A4' NOT NULL,
	"min_account_age" integer DEFAULT 16 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "localization"."translations" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"entity_type" text NOT NULL,
	"entity_key" text NOT NULL,
	"language" text NOT NULL,
	"fields" jsonb NOT NULL,
	"status" text DEFAULT 'draft' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "availability"."holiday_dates" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"holiday_slug" text NOT NULL,
	"year" integer NOT NULL,
	"date" date NOT NULL
);
--> statement-breakpoint
CREATE TABLE "availability"."holidays" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"sort_order" integer NOT NULL,
	"countries" text[] NOT NULL,
	"fixed_month" integer,
	"fixed_day" integer,
	"lead_days" integer DEFAULT 0 NOT NULL,
	"after_days" integer DEFAULT 0 NOT NULL,
	"approximate" boolean DEFAULT false NOT NULL,
	"label" text
);
--> statement-breakpoint
CREATE TABLE "availability"."plate_rules" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"plate_slug" text NOT NULL,
	"mode" text NOT NULL,
	"countries" text[] DEFAULT '{}'::text[] NOT NULL,
	"valid_from" date,
	"valid_to" date
);
--> statement-breakpoint
CREATE TABLE "availability"."seasons" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"countries" text[] NOT NULL,
	"from_month" integer NOT NULL,
	"from_day" integer NOT NULL,
	"to_month" integer NOT NULL,
	"to_day" integer NOT NULL,
	"plate_slugs" text[] NOT NULL
);
--> statement-breakpoint
CREATE TABLE "analytics"."daily_totals" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"plate_slug" text NOT NULL,
	"market" text NOT NULL,
	"country" text NOT NULL,
	"page_views" integer DEFAULT 0 NOT NULL,
	"plate_views" integer DEFAULT 0 NOT NULL,
	"downloads" integer DEFAULT 0 NOT NULL,
	"prints" integer DEFAULT 0 NOT NULL,
	"completions" integer DEFAULT 0 NOT NULL,
	"unique_visitors" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "analytics"."events" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"type" text NOT NULL,
	"plate_slug" text,
	"market" text NOT NULL,
	"country" text,
	"device" text NOT NULL,
	"visitor_hash" text,
	"occurred_at" timestamp with time zone NOT NULL
);
--> statement-breakpoint
ALTER TABLE "catalog"."plate_versions" ADD CONSTRAINT "plate_versions_plate_id_plates_id_fk" FOREIGN KEY ("plate_id") REFERENCES "catalog"."plates"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "ages_tenant_slug" ON "catalog"."ages" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "categories_tenant_slug" ON "catalog"."categories" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "continents_tenant_slug" ON "catalog"."continents" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "plate_versions_plate_version" ON "catalog"."plate_versions" USING btree ("plate_id","version");--> statement-breakpoint
CREATE UNIQUE INDEX "plates_tenant_slug" ON "catalog"."plates" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "markets_tenant_code" ON "localization"."markets" USING btree ("tenant_id","code");--> statement-breakpoint
CREATE UNIQUE INDEX "translations_unique" ON "localization"."translations" USING btree ("tenant_id","entity_type","entity_key","language");--> statement-breakpoint
CREATE UNIQUE INDEX "holiday_dates_unique" ON "availability"."holiday_dates" USING btree ("tenant_id","holiday_slug","year");--> statement-breakpoint
CREATE UNIQUE INDEX "holidays_tenant_slug" ON "availability"."holidays" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "plate_rules_tenant_plate" ON "availability"."plate_rules" USING btree ("tenant_id","plate_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "seasons_tenant_slug" ON "availability"."seasons" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "daily_totals_unique" ON "analytics"."daily_totals" USING btree ("tenant_id","day","plate_slug","market","country");--> statement-breakpoint
CREATE INDEX "events_tenant_time" ON "analytics"."events" USING btree ("tenant_id","occurred_at");