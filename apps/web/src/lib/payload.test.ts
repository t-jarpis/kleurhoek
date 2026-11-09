import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { cardOf, packCard, unpackCard, type CardData } from "./cards";
import type { PlateItem, Taxonomy } from "./types";

const SRC = join(__dirname, "..");
const files = (dir: string): string[] => readdirSync(dir).flatMap((n) => {
  const p = join(dir, n);
  return statSync(p).isDirectory() ? files(p) : /\.tsx$/.test(n) ? [p] : [];
});
const isClient = (s: string) => /^\s*["']use client["']/.test(s);

/**
 * ADR 0099: de lijst van alle platen gaat niet als prop naar een client component. Wat een client component
 * als prop krijgt, staat in elke pagina een tweede keer (RSC-payload); zo werd de voorpagina 400 kB.
 */
describe("kleine pagina's (ADR 0099)", () => {
  it("server components geven geen platenlijst (plates, slugs) aan een client component", () => {
    const wrong: string[] = [];
    for (const file of [...files(join(SRC, "app")), ...files(join(SRC, "components"))]) {
      const s = readFileSync(file, "utf8");
      if (isClient(s)) continue;
      for (const m of s.matchAll(/<([A-Z]\w*)\b[^>]*?\b(plates|slugs)=\{/g)) {
        const name = m[1]!;
        const from = new RegExp(`import\\s*\\{[^}]*\\b${name}\\b[^}]*\\}\\s*from\\s*["'](?:@/components/|\\./)(\\w+)["']`).exec(s)?.[1];
        if (!from) continue;
        if (isClient(readFileSync(join(SRC, "components", `${from}.tsx`), "utf8"))) wrong.push(`${file.slice(SRC.length)}: <${name} ${m[2]}=…>`);
      }
    }
    expect(wrong).toEqual([]);
  });

  it("de voorpagina laadt de platenlijst vooruit en Browse haalt hem op", () => {
    const home = readFileSync(join(SRC, "app/[org]/[market]/page.tsx"), "utf8");
    expect(home).toMatch(/preload\(plateIndexPath\(base\), \{ as: "fetch", crossOrigin: "anonymous" \}\)/);
    expect(readFileSync(join(SRC, "components/Browse.tsx"), "utf8")).toMatch(/usePlates\(/);
  });

  it("platen.json wordt bewaard zoals de pagina's (ISR, ADR 0093)", () => {
    const route = readFileSync(join(SRC, "app/[org]/[market]/platen.json/route.ts"), "utf8");
    expect(route).toMatch(/export const revalidate = \d+/);
    expect(route).toMatch(/generateStaticParams/);
    expect(route).not.toMatch(/\bheaders\(|\bcookies\(|searchParams/);
  });
});

const taxonomy: Taxonomy = {
  categories: [{ slug: "dieren", color: "#e2483d", name: "Dieren" }], ages: [], continents: [], holidays: [], goals: [], learningFilters: false,
};
const plate = (p: Partial<PlateItem>): PlateItem => ({ slug: "kat", name: "Kat op een kussen", category: "dieren", age: "4-6", world: null, holiday: null, svg: "/v1/assets/plates/kat/1.svg", kind: "kleurplaat", goals: [], ...p });

describe("kaarten als korte rij (ADR 0099)", () => {
  it("komt na inpakken en uitpakken hetzelfde terug", () => {
    const cases: CardData[] = [
      cardOf(plate({}), taxonomy, "alle"),
      cardOf(plate({ svg: "/v1/assets/plates/kat/3.de-ab12cd.svg" }), taxonomy, "alle", { kindLabel: "Knipplaat", alt: "Kat – knipplaat" }),
      cardOf(plate({}), taxonomy, "alle", { alt: "Kat – kleurplaat" }),
      cardOf(plate({ svg: "/elders/kat.svg" }), taxonomy, "alle", { kindLabel: "Spel" }),
    ];
    for (const c of cases) expect(unpackCard(JSON.parse(JSON.stringify(packCard(c))))).toEqual(c);
  });

  it("laat het vaste begin van het svg-adres en een alt gelijk aan de naam weg", () => {
    expect(packCard(cardOf(plate({}), taxonomy, "alle", { alt: "Kat op een kussen" }))).toEqual(["kat", "Kat op een kussen", "1.svg", "Dieren", "#e2483d", "4-6"]);
  });

  it("is per kaart klein", () => {
    const row = packCard(cardOf(plate({}), taxonomy, "alle", { alt: "Kat op een kussen – kleurplaat" }));
    expect(JSON.stringify(row).length).toBeLessThan(120);
  });
});
