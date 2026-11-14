import { afterEach, describe, expect, it, vi } from "vitest";
import { openPrint, resetPrintGuard } from "./print";

describe("openPrint", () => {
  afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); resetPrintGuard(); });
  it("opent het printvenster niet twee keer kort na elkaar", () => {
    vi.useFakeTimers();
    const print = vi.fn();
    vi.stubGlobal("window", { print, addEventListener: vi.fn(), removeEventListener: vi.fn() });
    expect(openPrint()).toBe(true);
    vi.advanceTimersByTime(2000);
    expect(openPrint()).toBe(false);
    vi.advanceTimersByTime(3500);
    expect(openPrint()).toBe(true);
    expect(print).toHaveBeenCalledTimes(2);
  });
});
