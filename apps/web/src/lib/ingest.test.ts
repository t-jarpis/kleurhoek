import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));
const { send } = await import("./ingest");

/** Tellen bij een haperende API (ADR 0082): opnieuw proberen, en een fout in het event niet. */
describe("send", () => {
  afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

  it("probeert opnieuw na een 503 en lukt de derde keer", async () => {
    const f = vi.fn().mockResolvedValueOnce(new Response(null, { status: 503 })).mockRejectedValueOnce(new Error("reset")).mockResolvedValueOnce(new Response(null, { status: 202 }));
    vi.stubGlobal("fetch", f);
    expect(await send("[]", "print", [0, 0])).toBe(true);
    expect(f).toHaveBeenCalledTimes(3);
  });

  it("geeft een ongeldig event niet opnieuw door, en logt één regel als het niet lukt", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const f = vi.fn().mockResolvedValue(new Response(null, { status: 400 }));
    vi.stubGlobal("fetch", f);
    expect(await send("[]", "print", [0, 0])).toBe(false);
    expect(f).toHaveBeenCalledTimes(1);
    expect(warn).toHaveBeenCalledWith(expect.stringContaining("HTTP 400"));
  });
});
