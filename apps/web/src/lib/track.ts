"use client";

/** Soort pagina bij page_view (ADR 0020): nooit het adres zelf. */
export type PageKind = "home" | "plaat" | "boekje" | "account" | "niet-gevonden" | "disclaimer" | "contact" | "themas" | "thema" | "eigen-omgeving";
export type TrackEvent = { type: "page_view" | "plate_view" | "plate_colored" | "plate_completed" | "pdf_download" | "print" | "materials_view"; market: string; plate?: string; page?: PageKind };

/** Domeinen die naar de site doorsturen met ?via=<code> (ADR 0032). */
const ENTRY = new Set(["be", "com"]);
let landed = false;

/**
 * Binnenkomst (ADR 0032), alleen bij de eerste paginaweergave van een bezoek van buitenaf: via welk domein
 * (kleurhoek.nl, .be, .com) en van welke site (alleen de hostnaam van de verwijzer, geen pad). Daarna gaat
 * ?via= uit de adresbalk, zodat het niet in gedeelde links belandt.
 */
function landing(): { entry: string; ref: string } | null {
  if (landed) return null;
  landed = true;
  let ref = "";
  try { ref = document.referrer ? new URL(document.referrer).hostname.toLowerCase().replace(/^www\./, "") : ""; } catch { ref = ""; }
  if (ref === location.hostname.replace(/^www\./, "") || /(^|\.)kleurhoek\.(nl|be|com)$/.test(ref)) return null; // intern
  const url = new URL(location.href);
  const via = url.searchParams.get("via") ?? "";
  if (url.searchParams.has("via")) { url.searchParams.delete("via"); history.replaceState(history.state, "", url.toString()); }
  return { entry: ENTRY.has(via) ? via : "nl", ref };
}

/** Stuurt een anonieme telling naar ons eigen domein. Geen cookies, geen scripts van derden. */
export function track(e: TrackEvent) {
  try {
    const land = e.type === "page_view" ? landing() : null;
    const body = JSON.stringify(land ? { ...e, ...land } : e);
    if (!navigator.sendBeacon?.("/e", new Blob([body], { type: "text/plain" }))) {
      void fetch("/e", { method: "POST", body, keepalive: true, headers: { "content-type": "text/plain" } });
    }
  } catch { /* tellen mag nooit de site breken */ }
}
