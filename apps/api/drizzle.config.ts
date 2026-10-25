import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  schemaFilter: ["catalog", "localization", "availability", "analytics", "identity", "operations", "shop", "organizations", "contact", "sources", "messaging", "engagement"],
});
