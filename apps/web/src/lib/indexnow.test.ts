import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { INDEXNOW_KEY } from "./indexnow";

describe("IndexNow (ADR 0061)", () => {
  it("heeft een geldige sleutel, dezelfde als het aanmeldscript", () => {
    expect(INDEXNOW_KEY).toMatch(/^[a-f0-9]{32}$/);
    expect(readFileSync(join(__dirname, "../../../../scripts/indexnow.mjs"), "utf8")).toContain(`const KEY = "${INDEXNOW_KEY}"`);
  });
});
