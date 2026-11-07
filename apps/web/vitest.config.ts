import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

/** Zelfde `@/`-pad als Next, zodat ook modules met `@/`-imports te testen zijn. */
export default defineConfig({ resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } } });
