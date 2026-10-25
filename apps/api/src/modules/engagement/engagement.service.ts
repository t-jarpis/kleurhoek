import { Inject, Injectable } from "@nestjs/common";
import { and, asc, eq, inArray } from "drizzle-orm";
import { ENV, type Env } from "../../config/env";
import { DB, type Database } from "../../db/database";
import { withTenant } from "../../db/tenant";
import { CatalogService } from "../catalog/catalog.service";
import { favorites } from "./engagement.schema";

/** Zoveel favorieten per account; genoeg voor een jaar knutselen, en een grens tegen misbruik. */
export const MAX_FAVORITES = 500;

/**
 * Domein Betrokkenheid (ADR 0039): wat een account bewaart. Begint met favorieten. Alleen bestaande platen;
 * de volgorde is die van toevoegen.
 */
@Injectable()
export class EngagementService {
  constructor(@Inject(DB) private readonly db: Database, @Inject(ENV) private readonly env: Env, private readonly catalog: CatalogService) {}
  private get tenant() { return this.env.TENANT_ID; }

  async favorites(userId: string): Promise<string[]> {
    const rows = await withTenant(this.db, this.tenant, (tx) => tx.select({ slug: favorites.plateSlug }).from(favorites)
      .where(and(eq(favorites.tenantId, this.tenant), eq(favorites.userId, userId))).orderBy(asc(favorites.createdAt)));
    return rows.map((r) => r.slug);
  }

  /** Toevoegen (één of meer, bijvoorbeeld de favorieten van dit apparaat na het inloggen). Geeft de hele lijst. */
  async add(userId: string, slugs: string[]): Promise<string[]> {
    const published = new Set((await this.catalog.listPublished(this.tenant)).map((p) => p.slug));
    const current = await this.favorites(userId);
    const room = Math.max(0, MAX_FAVORITES - current.length);
    const fresh = [...new Set(slugs)].filter((s) => published.has(s) && !current.includes(s)).slice(0, room);
    if (fresh.length) {
      const now = Date.now();
      await withTenant(this.db, this.tenant, (tx) => tx.insert(favorites)
        .values(fresh.map((plateSlug, i) => ({ tenantId: this.tenant, userId, plateSlug, createdAt: new Date(now + i) }))).onConflictDoNothing());
    }
    return [...current, ...fresh];
  }

  async remove(userId: string, slugs: string[]): Promise<string[]> {
    if (slugs.length) await withTenant(this.db, this.tenant, (tx) => tx.delete(favorites).where(and(eq(favorites.tenantId, this.tenant), eq(favorites.userId, userId), inArray(favorites.plateSlug, slugs))));
    return this.favorites(userId);
  }

  /** Account verwijderd: alles van dit account weg (privacy, ADR 0002). */
  async forgetUser(userId: string) {
    await withTenant(this.db, this.tenant, (tx) => tx.delete(favorites).where(and(eq(favorites.tenantId, this.tenant), eq(favorites.userId, userId))));
  }
}
