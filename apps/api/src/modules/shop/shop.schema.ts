import { boolean, integer, jsonb, pgSchema, text, uniqueIndex } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const shopSchema = pgSchema("shop");

/**
 * Een winkel of partnerprogramma waar we naar doorverwijzen (bol, of een winkel zonder programma).
 * De koppeling (site-ID, sjabloon) beheert de eigenaar zelf in het admin panel.
 */
export const partners = shopSchema.table("partners", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  name: text("name").notNull(),
  enabled: boolean("enabled").notNull().default(false),
  /** Doorverwijs-URL met {url} (productpagina), {subId} (bron) en {sleutel} uit settings. */
  linkTemplate: text("link_template").notNull(),
  settings: jsonb("settings").$type<Record<string, string>>().notNull().default({}),
  /** Alleen productpagina's op deze domeinen; voorkomt dat we naar willekeurige sites doorsturen. */
  allowedHosts: text("allowed_hosts").array().notNull(),
  updatedBy: text("updated_by").notNull().default("systeem"),
}, (t) => [uniqueIndex("partners_tenant_slug").on(t.tenantId, t.slug)]);

/** Een product bij een partner. Naam en toelichting staan in Lokalisatie (entity "product"). */
export const products = shopSchema.table("products", {
  ...baseColumns(),
  slug: text("slug").notNull(),
  partnerSlug: text("partner_slug").notNull(),
  url: text("url").notNull(),
  ean: text("ean"),
  /** Indicatie zoals "ca. € 5"; geen echte prijs, die bepaalt de winkel. */
  priceHint: text("price_hint"),
  enabled: boolean("enabled").notNull().default(true),
  markets: text("markets").array().notNull(),
}, (t) => [uniqueIndex("products_tenant_slug").on(t.tenantId, t.slug)]);

/** Welk product we tonen bij een materiaal (laagste rank eerst). */
export const materialProducts = shopSchema.table("material_products", {
  ...baseColumns(),
  materialSlug: text("material_slug").notNull(),
  productSlug: text("product_slug").notNull(),
  rank: integer("rank").notNull().default(0),
}, (t) => [uniqueIndex("material_products_unique").on(t.tenantId, t.materialSlug, t.productSlug)]);
