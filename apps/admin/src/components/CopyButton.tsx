"use client";
import { useState } from "react";

/** CopyButton uit het design system: kopieert een waarde, meldt "Gekopieerd" en valt terug op selecteren. */
export function CopyButton({ value, label = "Kopieer", targetId }: { value: string; label?: string; targetId?: string }) {
  const [state, setState] = useState<"idle" | "done" | "manual">("idle");
  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setState("done");
    } catch {
      const el = targetId ? document.getElementById(targetId) : null;
      if (el) { const r = document.createRange(); r.selectNodeContents(el); const s = window.getSelection(); s?.removeAllRanges(); s?.addRange(r); }
      setState("manual");
    }
    setTimeout(() => setState("idle"), 2000);
  }
  return (
    <button type="button" className="ui-btn" data-variant="quiet" onClick={copy} aria-live="polite" aria-label={state === "idle" ? `${label}: ${value}` : undefined}>
      <svg className="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
        {state === "done" ? <path d="M5 12l5 5 9-10" /> : <><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V5a2 2 0 0 1 2-2h8" /></>}
      </svg>
      {state === "done" ? "Gekopieerd" : state === "manual" ? "Selecteer en kopieer" : "Kopieer"}
    </button>
  );
}
