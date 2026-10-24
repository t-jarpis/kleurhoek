ALTER TABLE "catalog"."plate_versions" ADD COLUMN "pages" jsonb DEFAULT '[]'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "catalog"."plates" ADD COLUMN "difficulty" integer;