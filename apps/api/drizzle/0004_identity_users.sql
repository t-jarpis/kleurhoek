CREATE TABLE "identity"."roles" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"permissions" text[] NOT NULL
);
--> statement-breakpoint
CREATE TABLE "identity"."user_roles" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"user_id" uuid NOT NULL,
	"role_slug" text NOT NULL,
	"granted_by" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "identity"."users" (
	"id" uuid PRIMARY KEY NOT NULL,
	"tenant_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	"zitadel_sub" text NOT NULL,
	"organization_id" text NOT NULL,
	"kind" text NOT NULL,
	"status" text DEFAULT 'active' NOT NULL,
	"display_name" text,
	"email" text,
	"locale" text,
	"country" text,
	"last_login_at" timestamp with time zone
);
--> statement-breakpoint
ALTER TABLE "identity"."user_roles" ADD CONSTRAINT "user_roles_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "identity"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "roles_tenant_slug" ON "identity"."roles" USING btree ("tenant_id","slug");--> statement-breakpoint
CREATE UNIQUE INDEX "user_roles_unique" ON "identity"."user_roles" USING btree ("tenant_id","user_id","role_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "users_tenant_sub" ON "identity"."users" USING btree ("tenant_id","zitadel_sub");--> statement-breakpoint
CREATE INDEX "users_tenant_kind" ON "identity"."users" USING btree ("tenant_id","kind","created_at");