import { describe, expect, it } from "vitest";
import { pickLanguage, t } from "../src/lib/i18n";
import { nl } from "../src/lib/messages";

describe("taal van de inlogpagina (ADR 0029)", () => {
  it("kiest eerst ui_locales, dan de browser, anders Nederlands", () => {
    expect(pickLanguage(["de-DE"], "fr-FR,fr;q=0.9")).toBe("de");
    expect(pickLanguage(undefined, "fr-BE,fr;q=0.9,en;q=0.8")).toBe("fr");
    expect(pickLanguage([], "ja-JP,pt;q=0.8")).toBe("nl");
    expect(pickLanguage(undefined, null)).toBe("nl");
  });
  it("heeft in elke taal dezelfde sleutels", () => {
    for (const lang of ["de", "en", "es", "fr", "it", "pl"]) {
      expect(Object.keys(t(lang)).sort()).toEqual(Object.keys(nl).sort());
      expect(t(lang).emailIntro("Kleurhoek")).toContain("Kleurhoek");
    }
  });
});
