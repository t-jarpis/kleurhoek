import { describe, expect, it } from "vitest";
import { edgeAllowed, fromWorker } from "./edge";

const secret = "s".repeat(48);

describe("edgeAllowed", () => {
  it("laat alles door zonder EDGE_SECRET (lokaal)", () => {
    expect(edgeAllowed("/nl-nl", null, undefined)).toBe(true);
    expect(edgeAllowed("/nl-nl", null, "")).toBe(true);
  });
  it("vereist de juiste header als EDGE_SECRET gezet is", () => {
    expect(edgeAllowed("/nl-nl", null, secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", "fout", secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", `${secret}x`, secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", secret.slice(1), secret)).toBe(false);
    expect(edgeAllowed("/nl-nl", secret, secret)).toBe(true);
  });
  it("houdt /healthz open voor de health checks", () => {
    expect(edgeAllowed("/healthz", null, secret)).toBe(true);
  });
});

describe("fromWorker", () => {
  it("vertrouwt de Worker alleen met het juiste geheim", () => {
    expect(fromWorker("geheim-van-de-worker", "geheim-van-de-worker", true)).toBe(true);
    expect(fromWorker("fout", "geheim-van-de-worker", true)).toBe(false);
    expect(fromWorker(null, "geheim-van-de-worker", true)).toBe(false);
  });
  it("zonder geheim: lokaal wel, in productie nooit", () => {
    expect(fromWorker(null, undefined, false)).toBe(true);
    expect(fromWorker("x", undefined, true)).toBe(false);
  });
});

describe("bots tellen niet mee", () => {
  it("herkent crawlers, headless browsers en scripts, niet gewone browsers", async () => {
    const { isBot } = await import("./bots");
    for (const ua of ["Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.0.0 Safari/537.36", "Mozilla/5.0 (compatible; bingbot/2.0)", "curl/8.4.0", "python-requests/2.31", "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.0)", "", "Mozilla/5.0 (compatible; AhrefsBot/7.0)"]) expect(isBot(ua)).toBe(true);
    for (const ua of ["Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"]) expect(isBot(ua)).toBe(false);
  });
});
