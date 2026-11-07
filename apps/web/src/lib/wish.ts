"use client";
import { fold } from "./search";

/**
 * Gezocht (ADR 0084): een gemist zoekwoord of een aanvraag naar /w. Elk woord één keer per soort per dag
 * per apparaat; wat al gevraagd is, onthoudt dit apparaat tot morgen (geen cookie, alleen deze browser).
 */
const KEY = "kh:gevraagd";
const sent = new Set<string>();
const today = () => new Date().toISOString().slice(0, 10);

function requestedToday(): string[] {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) ?? "null") as { day: string; terms: string[] } | null;
    return v?.day === today() ? v.terms : [];
  } catch { return []; }
}

/** Is dit woord vandaag op dit apparaat al aangevraagd? */
export function asked(term: string): boolean {
  return requestedToday().includes(fold(term));
}

export function sendWish(term: string, market: string, kind: "miss" | "request") {
  const key = `${kind}:${fold(term)}`;
  if (sent.has(key) || (kind === "request" && asked(term))) return;
  sent.add(key);
  if (kind === "request") {
    try { localStorage.setItem(KEY, JSON.stringify({ day: today(), terms: [...requestedToday(), fold(term)].slice(-50) })); } catch { /* geen opslag: dan alleen deze keer */ }
  }
  try {
    if (navigator.webdriver) return;
    const body = JSON.stringify({ term: term.trim().slice(0, 80), market, kind });
    if (!navigator.sendBeacon?.("/w", new Blob([body], { type: "text/plain" }))) {
      void fetch("/w", { method: "POST", body, keepalive: true, headers: { "content-type": "text/plain" } });
    }
  } catch { /* zoeken mag nooit de site breken */ }
}
