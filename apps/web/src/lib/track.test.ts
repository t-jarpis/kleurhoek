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
    trackPrint("nl-nl");
    trackPrint("nl-nl"); // beforeprint direct na de knop
    vi.advanceTimersByTime(6000);
    setPrintPlate(undefined);
    trackPrint("nl-nl"); // later: Ctrl+P op een pagina zonder studio
    await vi.waitFor(() => expect(sent).toHaveLength(2));
    expect(sent).toEqual([{ type: "print", market: "nl-nl", plate: "sinterklaas" }, { type: "print", market: "nl-nl" }]);
  });
});
