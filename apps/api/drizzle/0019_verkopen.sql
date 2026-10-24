CREATE TABLE "shop"."sales" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"import_id" uuid NOT NULL,
	"partner_slug" text NOT NULL,
	"day" date NOT NULL,
	"sub_id" text NOT NULL,
	"product_ref" text NOT NULL,
	"product_slug" text,
	"plate_slug" text,
	"orders" integer NOT NULL,
	"items" integer NOT NULL,
	"revenue_cents" integer NOT NULL,
	"commission_cents" integer NOT NULL,
	"currency" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "shop"."sales_imports" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"partner_slug" text NOT NULL,
	"file_name" text NOT NULL,
	"from_day" date NOT NULL,
	"to_day" date NOT NULL,
	"row_count" integer NOT NULL,
	"mapping" jsonb NOT NULL,
	"created_by" text NOT NULL
);
--> statement-breakpoint
ALTER TABLE "shop"."sales" ADD CONSTRAINT "sales_import_id_sales_imports_id_fk" FOREIGN KEY ("import_id") REFERENCES "shop"."sales_imports"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "sales_partner_day" ON "shop"."sales" USING btree ("tenant_id","partner_slug","day");--> statement-breakpoint
CREATE INDEX "sales_imports_partner" ON "shop"."sales_imports" USING btree ("tenant_id","partner_slug");--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.sales TO app_user;--> statement-breakpoint
ALTER TABLE shop.sales ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE shop.sales FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON shop.sales USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
--> statement-breakpoint
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.sales_imports TO app_user;--> statement-breakpoint
ALTER TABLE shop.sales_imports ENABLE ROW LEVEL SECURITY;--> statement-breakpoint
ALTER TABLE shop.sales_imports FORCE ROW LEVEL SECURITY;--> statement-breakpoint
CREATE POLICY tenant_isolation ON shop.sales_imports USING (tenant_id = current_setting('app.tenant_id', true)::uuid) WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
