import { boolean, customType, pgSchema, text, uniqueIndex, uuid, jsonb } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const organizationsSchema = pgSchema("organizations");

const bytea = customType<{ data: Buffer; driverData: Buffer }>({ dataType: () => "bytea" });

export const ORG_KINDS = ["platform", "school", "opvang", "vereniging", "bedrijf", "overig"] as const;
export type OrgKind = (typeof ORG_KINDS)[number];

/** Huisstijl: thema en lettertype uit @kleurhoek/theme, twee eigen kleuren, eigen naam of logo. */
export interface OrgBrand { theme: string | null; font: string | null; colors: { primary: string | null; accent: string | null }; wordmark: string | null; logoVersion: string | null }
/** Aanbod: welke platen en markten deze organisatie toont. null = alles. */
export interface OrgOffer { markets: string[] | null; categories: string[] | null; ages: string[] | null; kinds: ("kleurplaat" | "knutselen")[] | null }
export interface OrgFeatures { shop: boolean; accounts: boolean }
/**
 * Vindbaarheid (ADR 0035), alleen voor Kleurhoek zelf: verificatiecodes voor zoekmachines en per markt een eigen
 * titel en beschrijving voor de startpagina.
 */
export interface OrgSeo {
  googleVerification: string | null; bingVerification: string | null;
  home: Record<string, { title: string | null; description: string | null }>;
}

/**
 * Organisaties (ADR 0017): Kleurhoek zelf en whitelabel-partners zoals scholen en opvang. Elke
 * organisatie heeft een eigen (sub)domein, huisstijl en aanbod; de catalogus blijft van Kleurhoek.
 */
export const organizations = organizationsSchema.table("organizations", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  name: text("name").notNull(),
  kind: text("kind", { enum: ORG_KINDS }).notNull(),
  active: boolean("active").notNull().default(true),
  isDefault: boolean("is_default").notNull().default(false),
  hosts: text("hosts").array().notNull().default([]),
  brand: jsonb("brand").$type<OrgBrand>().notNull(),
  offer: jsonb("offer").$type<OrgOffer>().notNull(),
  features: jsonb("features").$type<OrgFeatures>().notNull(),
  seo: jsonb("seo").$type<OrgSeo>(),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("organizations_tenant_slug").on(t.tenantId, t.slug)]);

/** Logo-afbeelding (PNG, WebP, JPEG of SVG, max 256 kB). Los van de organisatie: groot en zelden nodig. */
export const organizationLogos = organizationsSchema.table("logos", {
  ...baseColumns(),
  organizationId: uuid("organization_id").notNull(),
  contentType: text("content_type").notNull(),
  sha256: text("sha256").notNull(),
  data: bytea("data").notNull(),
}, (t) => [uniqueIndex("logos_organization").on(t.tenantId, t.organizationId)]);
