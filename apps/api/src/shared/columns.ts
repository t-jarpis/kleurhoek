import { timestamp, uuid } from "drizzle-orm/pg-core";
import { uuidv7 } from "./uuid";

/** Velden die elke tabel heeft: id (UUIDv7), tenant en tijdstempels. */
export const baseColumns = () => ({
  id: uuid("id").primaryKey().$defaultFn(() => uuidv7()),
  tenantId: uuid("tenant_id").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});
