import { pgSchema, text, uniqueIndex, uuid } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const engagementSchema = pgSchema("engagement");

/**
 * Favorieten van een websiteaccount (ADR 0039): alleen welke platen, geen gedrag. Zonder account bewaart de site
 * ze op het apparaat; met een account staan ze hier, zodat ze op elk apparaat terugkomen.
 */
export const favorites = engagementSchema.table("favorites", {
  ...baseColumns(),
  userId: uuid("user_id").notNull(),
  plateSlug: text("plate_slug").notNull(),
}, (t) => [uniqueIndex("favorites_user_plate").on(t.tenantId, t.userId, t.plateSlug)]);
