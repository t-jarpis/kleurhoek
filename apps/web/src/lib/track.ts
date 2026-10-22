"use client";

export type TrackEvent = { type: "page_view" | "plate_view" | "plate_colored" | "plate_completed" | "pdf_download" | "print"; market: string; plate?: string };

/** Stuurt een anonieme telling naar ons eigen domein. Geen cookies, geen scripts van derden. */
export function track(e: TrackEvent) {
  try {
    const body = JSON.stringify(e);
    if (!navigator.sendBeacon?.("/e", new Blob([body], { type: "text/plain" }))) {
      void fetch("/e", { method: "POST", body, keepalive: true, headers: { "content-type": "text/plain" } });
    }
  } catch { /* tellen mag nooit de site breken */ }
}
