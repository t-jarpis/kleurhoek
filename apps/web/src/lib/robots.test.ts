import { describe, expect, it } from "vitest";
import { robots } from "./robots";

/** De groep van één user-agent, zoals een crawler hem leest. */
function group(txt: string, ua: string): string[] {
  const blocks = txt.split("\n\n").map((b) => b.split("\n"));
  return blocks.find((b) => b.includes(`User-agent: ${ua}`)) ?? [];
}

describe("robots.txt (ADR 0045, 0055)", () => {
  const txt = robots("www.kleurhoek.nl");
  it("weert trainers maar laat AI-zoekdiensten toe", () => {
    expect(group(txt, "GPTBot")).toContain("Disallow: /");
    expect(group(txt, "ClaudeBot")).toContain("Disallow: /");
    for (const ua of ["OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User", "PerplexityBot", "bingbot"]) {
      expect(group(txt, ua)).toContain("Allow: /");
      expect(group(txt, ua)).not.toContain("Disallow: /");
      expect(group(txt, ua)).toContain("Disallow: /auth/");
    }
  });
  it("wijst naar de sitemap van het eigen domein", () => expect(txt).toContain("Sitemap: https://www.kleurhoek.nl/sitemap.xml"));
});
