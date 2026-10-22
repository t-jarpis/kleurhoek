CREATE SCHEMA "shop";
--> statement-breakpoint
CREATE TABLE "catalog"."materials" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"sort_order" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "catalog"."plate_materials" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"plate_id" uuid NOT NULL,
	"material_slug" text NOT NULL,
	"optional" boolean DEFAULT false NOT NULL,
	"sort_order" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "analytics"."daily_product_clicks" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"day" date NOT NULL,
	"product_slug" text NOT NULL,
	"plate_slug" text NOT NULL,
	"market" text NOT NULL,
	"country" text NOT NULL,
	"clicks" integer DEFAULT 0 NOT NULL,
	"unique_visitors" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "shop"."material_products" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"material_slug" text NOT NULL,
	"product_slug" text NOT NULL,
	"rank" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "shop"."partners" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"enabled" boolean DEFAULT false NOT NULL,
	"link_template" text NOT NULL,
	"settings" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"allowed_hosts" text[] NOT NULL,
	"updated_by" text DEFAULT 'systeem' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "shop"."products" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"partner_slug" text NOT NULL,
	"url" text NOT NULL,
	"ean" text,
	"price_hint" text,
	"enabled" boolean DEFAULT true NOT NULL,
	"markets" text[] NOT NULL
);
--> statement-breakpoint
ALTER TABLE "catalog"."plate_versions" ADD COLUMN "height" integer DEFAULT 200 NOT NULL;--> statement-breakpoint
ALTER TABLE "catalog"."plates" ADD COLUMN "kind" text DEFAULT 'kleurplaat' NOT NULL;--> statement-breakpoint
ALTER TABLE "catalog"."plates" ADD COLUMN "minutes" integer;--> statement-breakpoint
ALTER TABLE "catalog"."plates" ADD COLUMN "adult_help" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "catalog"."plates" ADD COLUMN "paper_gsm" integer;--> statement-breakpoint
ALTER TABLE "analytics"."daily_totals" ADD COLUMN "materials_views" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "analytics"."daily_totals" ADD COLUMN "product_clicks" integer DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "analytics"."events" ADD COLUMN "product_slug" text;--> statement-breakpoint
ALTER TABLE "catalog"."plate_materials" ADD CONSTRAINT "plate_materials_plate_id_plates_id_fk" FOREIGN KEY ("plate_id") REFERENCES "catalog"."plates"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "materials_tenant_slug" ON "catalog"."materials" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "plate_materials_unique" ON "catalog"."plate_materials" USING btree ("tenant_id","plate_id","material_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "daily_product_clicks_unique" ON "analytics"."daily_product_clicks" USING btree ("tenant_id","day","product_slug","plate_slug","market","country");--> statement-breakpoint
CREATE UNIQUE INDEX "material_products_unique" ON "shop"."material_products" USING btree ("tenant_id","material_slug","product_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "partners_tenant_slug" ON "shop"."partners" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "products_tenant_slug" ON "shop"."products" USING btree ("tenant_id","slug");