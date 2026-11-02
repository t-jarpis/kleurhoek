import { describe, expect, it } from "vitest";
import { DEFAULT_TEMPLATES } from "../src/modules/messaging/defaults";
import { ROW_COUNT_OK } from "../src/modules/messaging/defaults-i18n";
import { TEMPLATE_LANGUAGES } from "../src/modules/messaging/messaging.types";
import { MAIL_LANGUAGES, renderMail } from "../src/modules/messaging/render";
import { lastScheduled } from "../src/modules/messaging/workflows.service";
import { preferenceToken, readPreferenceToken } from "../src/modules/messaging/tokens";

const links = { site: "https://www.kleurhoek.test/nl-nl", preferences: "https://www.kleurhoek.test/nl-nl/mail?t=x", unsubscribe: "https://www.kleurhoek.test/nl-nl/mail?t=x&afmelden=1" };

describe("mail opmaken (ADR 0037)", () => {
  it("maakt HTML en tekst in de taal van de mail, met terugval op Nederlands als er geen Engels is, en zonder losse scripts", () => {
    const m = renderMail({
      subject: { nl: "Hallo", de: "Hallo DE" }, preheader: {}, language: "de", links, topics: ["nieuwe-platen"],
      blocks: [
        { id: "h", type: "heading", text: { nl: "Kop <script>" } },
        { id: "t", type: "text", text: { nl: "Een **vette** [link](https://example.test)\n\nen [stout](javascript:alert(1))" } },
        { id: "b", type: "button", label: { nl: "Ga" }, url: "{{site}}" },
        { id: "p", type: "plates", source: "new", max: 2, columns: 2 },
      ],
      plates: { p: [{ name: "Egel", url: "https://www.kleurhoek.test/nl-nl/platen/egel", image: "https://www.kleurhoek.test/v1/assets/plates/egel/1.png" }] },
    });
    expect(m.subject).toBe("Hallo DE");
    expect(m.html).toContain("Kop &lt;script&gt;");
    expect(m.html).toContain("<strong>vette</strong>");
    expect(m.html).not.toContain("javascript:");
    expect(m.html).toContain('href="https://www.kleurhoek.test/nl-nl"');
    expect(m.html).toContain("1.png");
    expect(m.html).toMatch(/Abmelden/);
    expect(m.html).not.toMatch(/var\(--/);
    expect(m.text).toContain("- Egel: https://www.kleurhoek.test/nl-nl/platen/egel");
    expect(m.text).toContain("Abmelden: https://www.kleurhoek.test/nl-nl/mail?t=x&afmelden=1");
  });

  it("zet geen afmeldlinks in een bevestigingsmail", () => {
    const m = renderMail({ subject: { nl: "Bevestig" }, preheader: {}, language: "nl", links: { ...links, confirm: "https://c" }, topics: [], transactional: true, plates: {},
      blocks: [{ id: "b", type: "button", label: { nl: "Bevestigen" }, url: "{{bevestigen}}" }] });
    expect(m.html).toContain('href="https://c"');
    expect(m.html).not.toContain("Afmelden");
  });
});

describe("links en planning", () => {
  it("maakt en controleert voorkeurtokens", () => {
    const id = "0192f6a0-1234-7000-8000-00000000abcd";
    const t = preferenceToken("s".repeat(40), id);
    expect(readPreferenceToken("s".repeat(40), t)).toBe(id);
    expect(readPreferenceToken("x".repeat(40), t)).toBeNull();
    expect(readPreferenceToken("s".repeat(40), `${t.slice(0, -1)}A`)).toBeNull();
  });

  it("vindt de laatste maandag 8:00 in Amsterdam", () => {
    // Woensdag 21 oktober 2026, 12:00 UTC (14:00 in Amsterdam, zomertijd).
    expect(lastScheduled(1, 8, new Date("2026-10-21T12:00:00Z")).toISOString()).toBe("2026-10-19T06:00:00.000Z");
    // Maandag 7:00 in Amsterdam: nog niet, dus de week ervoor.
    expect(lastScheduled(1, 8, new Date("2026-10-19T05:00:00Z")).toISOString()).toBe("2026-10-12T06:00:00.000Z");
    // Winter: maandag 7 december 2026, 10:00 UTC.
    expect(lastScheduled(1, 8, new Date("2026-12-07T10:00:00Z")).toISOString()).toBe("2026-12-07T07:00:00.000Z");
  });
});

describe("mail in alle talen", () => {
  it("elke standaardtemplate staat in elke taal van de site, behalve wat maar in één taal bestaat", () => {
    expect(ROW_COUNT_OK()).toEqual([]);
    expect(MAIL_LANGUAGES).toHaveLength(29);
    for (const t of DEFAULT_TEMPLATES) {
      const langs = TEMPLATE_LANGUAGES[t.slug] ?? MAIL_LANGUAGES;
      const texts = [t.subject, ...t.blocks.flatMap((b) => ("text" in b ? [b.text] : "label" in b ? [b.label] : []))];
      for (const text of texts) expect(langs.filter((l) => !text[l]), `${t.slug}: ${text.nl}`).toEqual([]);
    }
  });

  it("ontbreekt een taal, dan Engels, ook in de voettekst", () => {
    const m = renderMail({ subject: { nl: "Hallo", en: "Hello" }, preheader: {}, language: "xx", links, topics: ["nieuwe-platen"], plates: {}, blocks: [] });
    expect(m.subject).toBe("Hello");
    expect(m.text).toContain("Unsubscribe");
    const sv = renderMail({ subject: { nl: "Hallo" }, preheader: {}, language: "sv", links, topics: ["nieuwe-platen", "feestdagen"], plates: {}, blocks: [] });
    expect(sv.text).toContain("nya bilder och högtider");
  });
});
