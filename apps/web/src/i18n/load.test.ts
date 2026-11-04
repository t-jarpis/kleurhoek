import { describe, expect, it } from "vitest";
import { LIVE_MARKETS } from "../lib/markets";
import { loadMessages } from "./load";
import { messages } from "./nl";
import { LANGUAGES } from "./variants";

/** De browser laadt per taal (ADR 0081); dat moet precies dezelfde teksten geven als de server. */
describe("teksten per taal in de browser", () => {
  it("geeft voor elke markt en taal hetzelfde als messages()", async () => {
    for (const key of [...LIVE_MARKETS, ...LANGUAGES, "xx-yy"]) {
      const browser = await loadMessages(key), server = messages(key);
      expect(JSON.stringify(browser), key).toBe(JSON.stringify(server));
      expect(browser.metaPlate("Kat", "Kleurplaat A4"), key).toBe(server.metaPlate("Kat", "Kleurplaat A4"));
    }
  });
  it("laadt elke taal maar één keer per markt", async () => {
    expect(loadMessages("en-us")).toBe(loadMessages("EN-US"));
    expect((await loadMessages("en-us")).kindNames.kleurplaat).toBe("Coloring page");
  });
});
