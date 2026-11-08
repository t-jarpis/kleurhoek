"use client";
import { useEffect } from "react";
import { trackPrint } from "@/lib/track";

/** Telt elke print, ook via Ctrl+P, het browsermenu of de knoppen bij cadeaulabels (ADR 0020). */
export function PrintTracker({ market }: { market: string }) {
  useEffect(() => {
    const on = () => trackPrint(market);
    window.addEventListener("beforeprint", on);
    return () => window.removeEventListener("beforeprint", on);
  }, [market]);
  return null;
}
