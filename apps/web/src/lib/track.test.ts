import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setPrintPlate, trackPrint } from "./track";

describe("prints tellen (ADR 0020)", () => {
  const sent: unknown[] = [];
  beforeEach(() => {
    vi.useFakeTimers();
    sent.length = 0;
    vi.stubGlobal("navigator", { webdriver: false, sendBeacon: (_: string, b: Blob) => { void b.text().then((t) => sent.push(JSON.parse(t))); return true; } });
  });
  afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); setPrintPlate(undefined); });

  it("telt knop plus beforeprint één keer, met de open plaat erbij", async () => {
    setPrintPlate("sinterklaas");
    trackPrint("nl-nl", "button");
    trackPrint("nl-nl", "browser"); // beforeprint direct na de knop
    vi.advanceTimersByTime(20_000);
    trackPrint("nl-nl", "browser"); // Safari op iOS meldt beforeprint later nog eens
    trackPrint("nl-nl", "button"); // nog een keer printen met de knop telt wel
    vi.advanceTimersByTime(65_000);
    setPrintPlate(undefined);
    trackPrint("nl-nl", "browser"); // later: Ctrl+P op een pagina zonder studio
    await vi.waitFor(() => expect(sent).toHaveLength(3));
    expect(sent).toEqual([
      { type: "print", market: "nl-nl", plate: "sinterklaas" },
      { type: "print", market: "nl-nl", plate: "sinterklaas" },
      { type: "print", market: "nl-nl" },
    ]);
  });
});
