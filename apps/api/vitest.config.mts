import swc from "unplugin-swc";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [swc.vite({ module: { type: "es6" } })],
  test: { environment: "node", testTimeout: 60_000, hookTimeout: 60_000, include: ["src/**/*.test.ts", "test/**/*.test.ts"] },
});
