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

  private readonly glossaries = new Map<string, { at: number; map: Map<string, string> }>();

  /**
   * Woordenlijst voor de teksten in platen (ADR 0029): brontekst → vertaling. Een minuut in het geheugen,
   * want de zichtbaarheid van elke plaat hangt ervan af.
   */
  async glossary(tenantId: string, language: string, now = Date.now()): Promise<Map<string, string>> {
    const key = `${tenantId}:${language}`;
    const hit = this.glossaries.get(key);
    if (hit && now - hit.at < 60_000) return hit.map;
    const rows = await this.translate(tenantId, "text", language);
    const map = new Map<string, string>();
    for (const [src, fields] of rows) if (fields.text) map.set(src, fields.text);
    this.glossaries.set(key, { at: now, map });
    return map;
  }

  /** Vertaling opslaan of bijwerken (bijvoorbeeld de naam van een product uit het admin panel). */
  async save(tenantId: string, type: EntityType, key: string, language: string, fields: Fields): Promise<void> {
    await withTenant(this.db, tenantId, (tx) => tx.insert(translations)
      .values({ tenantId, entityType: type, entityKey: key, language, fields, status: "reviewed" })
      .onConflictDoUpdate({ target: [translations.tenantId, translations.entityType, translations.entityKey, translations.language], set: { fields, updatedAt: sql`now()` } }));
  }
}
