import { Inject, Injectable } from "@nestjs/common";
import { and, desc, eq, gte, lte, sql } from "drizzle-orm";
import type { AnyPgColumn } from "drizzle-orm/pg-core";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { CatalogService } from "../catalog/catalog.service";
import { AuditService } from "../identity/audit.service";
import { detectMapping, parseCsv, SALES_FIELDS, toRows, type SalesMapping, type SalesRow } from "./sales.import";
import { partners, products, sales, salesImports } from "./shop.schema";
import { ShopError } from "./shop.service";

/** Een rapport mag hooguit zo groot zijn (de API neemt tot 1 MB aan). */
export const MAX_CSV = 900_000;

/** Sub-ID die de site zelf meegeeft bij een doorklik (`kleurhoek-<plaat>`), zie /ga en ADR 0011. */
const PLATE_SUB = /^kleurhoek-([a-z0-9-]{1,64})$/;

/**
 * Verkopen uit rapporten van partners (ADR 0033): inlezen, herkennen welk product en welke plaat het was, en
 * optellen voor het admin panel. Doorkliks staan in Analytics; het admin panel legt ze naast elkaar.
 */
@Injectable()
export class SalesService {
  constructor(
    @Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env,
    private readonly audit: AuditService, private readonly catalog: CatalogService,
  ) {}

  /** Plaat uit de sub-ID, alleen als die plaat bestaat (een Amazon-tracking-ID als kleurhoek-21 is geen plaat). */
  private async plateOf(): Promise<(subId: string) => string | null> {
    const slugs = new Set((await this.catalog.listPublished(this.tenant)).map((p) => p.slug));
    return (subId) => { const m = PLATE_SUB.exec(subId)?.[1]; return m && slugs.has(m) ? m : null; };
  }

  private get tenant() { return this.env.TENANT_ID; }

  /** ASIN/EAN → product van deze partner. */
  private async productIndex(partner: string): Promise<Map<string, string>> {
    const rows = await withTenant(this.db, this.tenant, (tx) =>
      tx.select({ slug: products.slug, url: products.url, ean: products.ean }).from(products).where(eq(products.partnerSlug, partner)));
    const map = new Map<string, string>();
    for (const r of rows) {
      const asin = /\/dp\/([A-Z0-9]{10})/i.exec(r.url)?.[1];
      if (asin) map.set(asin.toUpperCase(), r.slug);
      if (r.ean) map.set(r.ean, r.slug);
    }
    return map;
  }

  /** De kolomkeuze van het vorige rapport van deze partner, als die kolommen ook in dit bestand staan. */
  private async lastMapping(partner: string, headers: string[]): Promise<SalesMapping | null> {
    const [last] = await withTenant(this.db, this.tenant, (tx) => tx.select({ mapping: salesImports.mapping }).from(salesImports)
      .where(eq(salesImports.partnerSlug, partner)).orderBy(desc(salesImports.createdAt)).limit(1));
    if (!last) return null;
    const m = last.mapping as SalesMapping;
    return SALES_FIELDS.every((f) => m[f] === null || m[f] === undefined || headers.includes(m[f]!)) ? m : null;
  }

  private async checkPartner(partner: string) {
    const [p] = await withTenant(this.db, this.tenant, (tx) => tx.select({ slug: partners.slug }).from(partners).where(eq(partners.slug, partner)).limit(1));
    if (!p) throw new ShopError("not_found", "Onbekende partner");
  }

  private async read(partner: string, csv: string, mapping?: SalesMapping) {
    if (csv.length > MAX_CSV) throw new ShopError("invalid", "Het bestand is te groot (hooguit 900 kB). Exporteer een kortere periode.");
    await this.checkPartner(partner);
    const parsed = parseCsv(csv);
    if (parsed.headers.length < 2) throw new ShopError("invalid", "Geen kolommen gevonden. Is dit een CSV-bestand?");
    const used = mapping ?? (await this.lastMapping(partner, parsed.headers)) ?? detectMapping(parsed.headers);
    for (const f of SALES_FIELDS) if (used[f] && !parsed.headers.includes(used[f]!)) throw new ShopError("invalid", `Kolom "${used[f]}" staat niet in het bestand`);
    if (!used.date || !used.commission) return { parsed, mapping: used, rows: [] as SalesRow[], skipped: parsed.rows.length };
    const { rows, skipped } = toRows(parsed, used);
    return { parsed, mapping: used, rows, skipped };
  }

  /** Voorbeeld: herkende kolommen, de eerste rijen en wat herkend is. Slaat niets op. */
  async preview(partner: string, csv: string, mapping?: SalesMapping) {
    const { parsed, mapping: used, rows, skipped } = await this.read(partner, csv, mapping);
    const [index, plateOf] = [await this.productIndex(partner), await this.plateOf()];
    const days = rows.map((r) => r.day).sort();
    return {
      headers: parsed.headers, mapping: used, sample: rows.slice(0, 5), total: rows.length, skipped,
      from: days[0] ?? null, to: days.at(-1) ?? null,
      matchedProducts: rows.filter((r) => index.has(r.product)).length,
      matchedPlates: rows.filter((r) => plateOf(r.subId)).length,
      problem: !used.date ? "Kies de kolom met de datum." : !used.commission ? "Kies de kolom met de commissie." : rows.length === 0 ? "Geen rijen met een datum en een commissie gevonden." : null,
    };
  }

  /**
   * Inlezen. Bestaande cijfers van deze partner in dezelfde periode worden vervangen, zodat een rapport
   * opnieuw inlezen (bijvoorbeeld na retouren) niets dubbel telt.
   */
  async import(actor: string, partner: string, fileName: string, csv: string, mapping: SalesMapping) {
    const { rows } = await this.read(partner, csv, mapping);
    if (!rows.length) throw new ShopError("invalid", "Geen rijen met een datum en een commissie gevonden.");
    const [index, plateOf] = [await this.productIndex(partner), await this.plateOf()];
    const days = rows.map((r) => r.day).sort();
    const from = days[0]!, to = days.at(-1)!;
    // Optellen per dag, sub-ID, product en valuta.
    const grouped = new Map<string, { r: SalesRow; orders: number; items: number; revenue: number; commission: number }>();
    for (const r of rows) {
      const key = [r.day, r.subId, r.product, r.currency].join("\u0000");
      const g = grouped.get(key) ?? { r, orders: 0, items: 0, revenue: 0, commission: 0 };
      g.orders++; g.items += r.items; g.revenue += r.revenueCents; g.commission += r.commissionCents;
      grouped.set(key, g);
    }
    const result = await withTenant(this.db, this.tenant, async (tx) => {
      await tx.delete(sales).where(and(eq(sales.partnerSlug, partner), gte(sales.day, from), lte(sales.day, to)));
      const [imp] = await tx.insert(salesImports).values({
        tenantId: this.tenant, partnerSlug: partner, fileName: fileName.slice(0, 200) || "rapport.csv", fromDay: from, toDay: to, rowCount: rows.length, mapping, createdBy: actor,
      }).returning({ id: salesImports.id });
      const values = [...grouped.values()].map((g) => ({
        tenantId: this.tenant, importId: imp!.id, partnerSlug: partner, day: g.r.day, subId: g.r.subId, productRef: g.r.product,
        productSlug: index.get(g.r.product) ?? null, plateSlug: plateOf(g.r.subId),
        orders: g.orders, items: g.items, revenueCents: g.revenue, commissionCents: g.commission, currency: g.r.currency,
      }));
      for (let i = 0; i < values.length; i += 1000) await tx.insert(sales).values(values.slice(i, i + 1000));
      await this.audit.record(tx, this.tenant, { actor, action: "shop.sales.imported", subject: `partner:${partner}`, after: { fileName, from, to, rows: rows.length } });
      return { importId: imp!.id, from, to, rows: rows.length };
    });
    return result;
  }

  /** Verkopen in een periode: per partner en valuta, per product, en de laatste rapporten. */
  async report(from: string, to: string) {
    return withTenant(this.db, this.tenant, async (tx) => {
      const inRange = and(eq(sales.tenantId, this.tenant), gte(sales.day, from), lte(sales.day, to));
      const sum = (c: AnyPgColumn) => sql<number>`coalesce(sum(${c}), 0)::int`;
      const byPartner = await tx.select({
        partner: sales.partnerSlug, currency: sales.currency, orders: sum(sales.orders), items: sum(sales.items),
        revenueCents: sum(sales.revenueCents), commissionCents: sum(sales.commissionCents),
      }).from(sales).where(inRange).groupBy(sales.partnerSlug, sales.currency).orderBy(desc(sum(sales.commissionCents)));
      const byProduct = await tx.select({
        product: sql<string>`coalesce(${sales.productSlug}, ${sales.productRef})`, matched: sql<boolean>`${sales.productSlug} is not null`,
        partner: sales.partnerSlug, currency: sales.currency, orders: sum(sales.orders), items: sum(sales.items), commissionCents: sum(sales.commissionCents),
      }).from(sales).where(inRange).groupBy(sql`1`, sql`2`, sales.partnerSlug, sales.currency).orderBy(desc(sum(sales.commissionCents))).limit(50);
      const byPlate = await tx.select({ plate: sales.plateSlug, orders: sum(sales.orders), commissionCents: sum(sales.commissionCents), currency: sales.currency })
        .from(sales).where(and(inRange, sql`${sales.plateSlug} is not null`)).groupBy(sales.plateSlug, sales.currency).orderBy(desc(sum(sales.commissionCents))).limit(20);
      // Tot welke dag elk partnerrapport loopt (alle rapporten, niet alleen deze periode).
      const coverage = await tx.select({ partner: salesImports.partnerSlug, lastDay: sql<string>`max(${salesImports.toDay})::text` })
        .from(salesImports).where(eq(salesImports.tenantId, this.tenant)).groupBy(salesImports.partnerSlug);
      const imports = await tx.select({
        id: salesImports.id, partner: salesImports.partnerSlug, fileName: salesImports.fileName, from: sql<string>`${salesImports.fromDay}::text`,
        to: sql<string>`${salesImports.toDay}::text`, rows: salesImports.rowCount, by: salesImports.createdBy, at: salesImports.createdAt,
      }).from(salesImports).where(eq(salesImports.tenantId, this.tenant)).orderBy(desc(salesImports.createdAt)).limit(10);
      return { from, to, byPartner, byProduct, byPlate, coverage, imports };
    });
  }
}
