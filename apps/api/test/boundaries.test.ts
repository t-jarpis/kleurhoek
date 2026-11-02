import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, normalize, relative } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * Grenzen tussen domeinen (ADR 0001, 0066): elk domein heeft een AGENTS.md met wat publiek is. Een ander domein
 * mag alleen die bestanden importeren. Zo blijven tabellen en interne helpers van een domein van dat domein.
 */
const ROOT = join(__dirname, "../src/modules");
const domains = readdirSync(ROOT).filter((d) => statSync(join(ROOT, d)).isDirectory());

const files = (dir: string): string[] => readdirSync(dir).flatMap((f) => {
  const p = join(dir, f);
  return statSync(p).isDirectory() ? files(p) : p.endsWith(".ts") ? [p] : [];
});

function publicOf(domain: string): Set<string> {
  const md = readFileSync(join(ROOT, domain, "AGENTS.md"), "utf8");
  const section = md.split(/^## Publiek\s*$/m)[1]?.split(/^## /m)[0] ?? "";
  return new Set([...section.matchAll(/^- `([^`]+)`/gm)].map((m) => m[1]!));
}

describe("grenzen tussen domeinen", () => {
  it("elk domein heeft een AGENTS.md met een lijst publieke bestanden", () => {
    for (const d of domains) expect(() => publicOf(d), d).not.toThrow();
  });

  it("andere domeinen importeren alleen wat publiek is", () => {
    const pub = new Map(domains.map((d) => [d, publicOf(d)]));
    const wrong: string[] = [];
    for (const d of domains) {
      for (const file of files(join(ROOT, d))) {
        for (const [, spec] of readFileSync(file, "utf8").matchAll(/from "(\.{1,2}\/[^"]+)"/g)) {
          const target = relative(ROOT, normalize(join(dirname(file), spec!)));
          const [other, ...rest] = target.split("/");
          if (!other || other === d || !domains.includes(other)) continue;
          const name = `${rest.join("/")}.ts`;
          if (!pub.get(other)!.has(name)) wrong.push(`${relative(ROOT, file)} → ${other}/${name}`);
        }
      }
    }
    expect(wrong).toEqual([]);
  });
});
