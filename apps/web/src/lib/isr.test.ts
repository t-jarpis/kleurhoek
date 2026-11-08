import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const ROOT = join(__dirname, "../app/[org]/[market]");
const pages = (dir: string): string[] => readdirSync(dir).flatMap((n) => {
  const p = join(dir, n);
  return statSync(p).isDirectory() ? pages(p) : n === "page.tsx" ? [p] : [];
});

/** ADR 0093: bewaarde pagina's (ISR) mogen niets per verzoek lezen; zulke pagina's zijn force-dynamic. */
describe("bewaarde pagina's (ADR 0093)", () => {
  it("een pagina die de link, cookies of headers leest, is force-dynamic", () => {
    const wrong = pages(ROOT).filter((p) => {
      const s = readFileSync(p, "utf8");
      return /\bsearchParams\b|\bcookies\(|\bheaders\(/.test(s) && !s.includes('dynamic = "force-dynamic"');
    });
    expect(wrong.map((p) => p.slice(ROOT.length))).toEqual([]);
  });

  it("de layout en elke [slug]-pagina hebben generateStaticParams", () => {
    const need = [join(ROOT, "layout.tsx"), ...pages(ROOT).filter((p) => p.includes("[slug]"))];
    expect(need.filter((p) => !readFileSync(p, "utf8").includes("generateStaticParams")).map((p) => p.slice(ROOT.length))).toEqual([]);
  });
});
