import { boolean, date, index, integer, jsonb, pgSchema, text, uniqueIndex, uuid } from "drizzle-orm/pg-core";
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

/**
 * Een ingelezen rapport van een partner (ADR 0033): welk bestand, welke periode, welke kolommen. De kolomkeuze
 * van het laatste rapport van een partner is het voorstel voor het volgende.
 */
export const salesImports = shopSchema.table("sales_imports", {
  ...baseColumns(),
  partnerSlug: text("partner_slug").notNull(),
  fileName: text("file_name").notNull(),
  fromDay: date("from_day", { mode: "string" }).notNull(),
  toDay: date("to_day", { mode: "string" }).notNull(),
  rowCount: integer("row_count").notNull(),
  mapping: jsonb("mapping").$type<Record<string, string | null>>().notNull(),
  createdBy: text("created_by").notNull(),
}, (t) => [index("sales_imports_partner").on(t.tenantId, t.partnerSlug)]);

/**
 * Verkopen per dag uit de rapporten van partners, opgeteld per sub-ID en product (ADR 0033). Bedragen in centen
 * in de valuta van het rapport. Product en plaat zijn herkend uit de ASIN/EAN en de sub-ID (`kleurhoek-<plaat>`).
 */
export const sales = shopSchema.table("sales", {
  ...baseColumns(),
  importId: uuid("import_id").notNull().references(() => salesImports.id, { onDelete: "cascade" }),
  partnerSlug: text("partner_slug").notNull(),
  day: date("day", { mode: "string" }).notNull(),
  subId: text("sub_id").notNull(),
  productRef: text("product_ref").notNull(),
  productSlug: text("product_slug"),
  plateSlug: text("plate_slug"),
  orders: integer("orders").notNull(),
  items: integer("items").notNull(),
  revenueCents: integer("revenue_cents").notNull(),
  commissionCents: integer("commission_cents").notNull(),
  currency: text("currency").notNull(),
}, (t) => [index("sales_partner_day").on(t.tenantId, t.partnerSlug, t.day)]);
