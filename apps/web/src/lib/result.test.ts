import fs from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ForParents } from "@/components/ForParents";
import { messages } from "@/i18n/nl";
import { LANGUAGES } from "@/i18n/variants";
import type { PlateDetail } from "./types";
import { svgInner } from "./svg";
import { resultSvg } from "./result";

const PLATES = path.resolve(__dirname, "../../../../packages/catalog-data/plates");
const read = (file: string) => fs.readFileSync(path.join(PLATES, file), "utf8");
const sheets = (slug: string) => fs.readdirSync(PLATES).filter((f) => f === `${slug}.svg` || f.startsWith(`${slug}.p`)).sort().map(read);
const WITH_RESULT = ["schoen-om-te-zetten", "bouwplaat-pakjesboot", "surprise-schoorsteendoosje", "surprise-mijterdoosje"];

describe("Zo wordt het (ADR 0100)", () => {
  it("haalt het plaatje uit vel 1 of een extra vel, als losse SVG met alt-tekst", () => {
    for (const slug of WITH_RESULT) {
      const [first, ...rest] = sheets(slug);
      const svg = resultSvg([svgInner(first!), ...rest], `${slug}: zo ziet het eruit`);
      expect(svg, slug).toMatch(/^<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" viewBox="[-\d. ]+" style="--sw:[\d.]+" role="img" aria-label="[^"]+">/);
      // Geen kleurvlak: het plaatje telt niet mee in de vlakken of online kleuren.
      expect(svg).not.toContain('class="r"');
      expect(svg).not.toContain("<text");
      expect(svg!.match(/<svg\b/g)).toHaveLength(1);
    }
  });

  it("geeft niets voor een plaat zonder plaatje", () => {
    expect(resultSvg([svgInner(read("pakjesboot.svg"))], "x")).toBeNull();
    expect(resultSvg([], "x")).toBeNull();
  });

  it("zet de alt-tekst veilig in het attribuut", () => {
    const svg = resultSvg(['<svg class="kh-result" x="1" y="2" width="3" height="4" viewBox="0 0 3 4" style="--sw:1.2"><path class="l" d="M0 0L3 4"/></svg>'], 'Doos "groot" & <klein>');
    expect(svg).toContain('aria-label="Doos &quot;groot&quot; &amp; &lt;klein>"');
    expect(svg).toContain('viewBox="0 0 3 4"');
    expect(svg).not.toMatch(/\s(x|y|width|height)="/);
  });

  it("staat naast de stappen in Voor ouders, en alleen als er een plaatje is", () => {
    const t = messages("nl-nl");
    const plate = { slug: "surprise-mijterdoosje", name: "Bouwplaat: mijterdoosje", kind: "bouwplaat", steps: ["Kleur", "Knip"], materials: [], pages: [],
      minutes: 30, difficulty: 2, adultHelp: true, paperGsm: 160, printNote: null } as unknown as PlateDetail;
    const svg = resultSvg(sheets("surprise-mijterdoosje").map(svgInner), t.resultAlt(plate.name))!;
    const html = renderToStaticMarkup(createElement(ForParents, { plate, market: "nl-nl", t, result: svg }));
    expect(html).toMatch(/<div class="kh-howto"><ol class="steps">.*<\/ol><figure class="kh-result-block" aria-labelledby="(result-[^"]+)"><h3 id="\1">Zo wordt het<\/h3><div class="kh-result-paper"><svg /);
    expect(html).toContain('aria-label="Bouwplaat: mijterdoosje: zo ziet het eruit als het klaar is"');
    const without = renderToStaticMarkup(createElement(ForParents, { plate, market: "nl-nl", t }));
    expect(without).not.toContain("kh-result");
    expect(without).toContain('<ol class="steps">');
  });

  it("heeft een titel en alt-tekst in elke taal", () => {
    for (const lang of LANGUAGES) {
      const t = messages(lang);
      expect(t.resultTitle, lang).toBeTruthy();
      expect(t.resultAlt("Doosje"), lang).toContain("Doosje");
    }
    expect(messages("en-us").resultAlt("Box")).toBe("Box: what it looks like when it's finished");
  });
});
