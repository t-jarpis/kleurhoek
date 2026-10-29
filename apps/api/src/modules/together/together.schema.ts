import { bigint, index, jsonb, pgSchema, text, timestamp, uniqueIndex, uuid, integer } from "drizzle-orm/pg-core";
import { baseColumns } from "../../shared/columns";

export const togetherSchema = pgSchema("together");

/**
 * Samen kleuren (ADR 0060): een kamer met een code van vier letters voor één plaat. Geen namen, geen accounts,
 * geen IP-adressen. Een kamer verdwijnt (met alles erin) als er een half uur niemand meer in zit.
 */
export const rooms = togetherSchema.table("rooms", {
  ...baseColumns(),
  code: text("code").notNull(),
  market: text("market").notNull(),
  plateSlug: text("plate_slug").notNull(),
  plateVersion: integer("plate_version").notNull(),
  activeAt: timestamp("active_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => [uniqueIndex("rooms_code").on(t.tenantId, t.code), index("rooms_active").on(t.activeAt)]);

/** Wat er in een kamer gebeurt, in volgorde: vullen, streken, ongedaan maken, opnieuw. */
export const roomOps = togetherSchema.table("room_ops", {
  ...baseColumns(),
  seq: bigint("seq", { mode: "number" }).generatedAlwaysAsIdentity(),
  roomId: uuid("room_id").notNull().references(() => rooms.id, { onDelete: "cascade" }),
  client: text("client").notNull(),
  body: jsonb("body").notNull(),
}, (t) => [index("room_ops_room_seq").on(t.roomId, t.seq)]);

/** Wie er nu in een kamer is (een willekeurige code per tabblad), voor "1 ander kleurt mee". */
export const roomPresence = togetherSchema.table("room_presence", {
  ...baseColumns(),
  roomId: uuid("room_id").notNull().references(() => rooms.id, { onDelete: "cascade" }),
  client: text("client").notNull(),
}, (t) => [uniqueIndex("room_presence_client").on(t.roomId, t.client)]);
