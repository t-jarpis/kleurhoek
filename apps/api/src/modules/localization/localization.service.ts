import { Inject, Injectable } from "@nestjs/common";
import { and, eq, inArray, sql } from "drizzle-orm";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { markets, translations, type EntityType } from "./localization.schema";

export interface Market { code: string; country: string; language: string; paperSize: "A4" | "Letter"; minAccountAge: number }
export type Fields = Record<string, string | null>;

const MARKET_CODE = /^[a-z]{2}-[A-Z]{2}$/;

@Injectable()
export class LocalizationService {
  constructor(@Inject(DB) private readonly db: Database) {}

  /** Alleen markten die live staan. Accepteert `nl-nl` en `nl-NL`. */
  async liveMarket(tenantId: string, code: string): Promise<Market | null> {
    const [lang, country] = code.split("-");
    const normalized = `${(lang ?? "").toLowerCase()}-${(country ?? "").toUpperCase()}`;
    if (!MARKET_CODE.test(normalized)) return null;
    const rows = await withTenant(this.db, tenantId, (tx) =>
      tx.select({ code: markets.code, country: markets.country, language: markets.language, paperSize: markets.paperSize, minAccountAge: markets.minAccountAge })
        .from(markets).where(and(eq(markets.tenantId, tenantId), eq(markets.code, normalized), eq(markets.status, "live"))).limit(1));
    return rows[0] ?? null;
  }

  /** Codes van alle markten die live staan, in kleine letters (zoals in de URL). */
  async liveMarkets(tenantId: string): Promise<string[]> {
    const rows = await withTenant(this.db, tenantId, (tx) =>
      tx.select({ code: markets.code }).from(markets).where(and(eq(markets.tenantId, tenantId), eq(markets.status, "live"))));
    return rows.map((r) => r.code.toLowerCase()).sort();
  }

  /** Vertalingen voor een soort ding in één taal. Sleutels zonder vertaling ontbreken in de map. */
  async translate(tenantId: string, type: EntityType, language: string, keys?: string[]): Promise<Map<string, Fields>> {
    const rows = await withTenant(this.db, tenantId, (tx) =>
      tx.select({ key: translations.entityKey, fields: translations.fields }).from(translations)
        .where(and(eq(translations.tenantId, tenantId), eq(translations.entityType, type), eq(translations.language, language),
          ...(keys ? [inArray(translations.entityKey, keys.length ? keys : [""])] : []))));
    return new Map(rows.map((r) => [r.key, r.fields]));
  }

  /** Vertaling opslaan of bijwerken (bijvoorbeeld de naam van een product uit het admin panel). */
  async save(tenantId: string, type: EntityType, key: string, language: string, fields: Fields): Promise<void> {
    await withTenant(this.db, tenantId, (tx) => tx.insert(translations)
      .values({ tenantId, entityType: type, entityKey: key, language, fields, status: "reviewed" })
      .onConflictDoUpdate({ target: [translations.tenantId, translations.entityType, translations.entityKey, translations.language], set: { fields, updatedAt: sql`now()` } }));
  }
}
