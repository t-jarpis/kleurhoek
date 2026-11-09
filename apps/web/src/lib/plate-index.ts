"use client";
import { useEffect, useState } from "react";
import { plateIndexPath } from "./sites";
import type { PlateItem } from "./types";

/**
 * De lijst van alle platen voor zoeken, filters, Verras me en de koelkast (ADR 0099). Niet meer in de HTML van de
 * voorpagina, maar één keer per bezoek opgehaald van `<markt>/platen.json` (bewaard als ISR, net als de pagina's).
 */
const loaded = new Map<string, Promise<PlateItem[]>>();

/** Eén verzoek per adres; mislukt het, dan probeert de volgende aanroep het opnieuw. */
export function loadPlates(base: string): Promise<PlateItem[]> {
  const url = plateIndexPath(base);
  let p = loaded.get(url);
  if (!p) {
    // Zelfde verzoek als de preload op de voorpagina (geen extra headers), zodat de browser dat antwoord hergebruikt.
    p = fetch(url)
      .then((r) => { if (!r.ok) throw new Error(`platen.json ${r.status}`); return r.json() as Promise<{ items: PlateItem[] }>; })
      .then((r) => r.items);
    p.catch(() => loaded.delete(url));
    loaded.set(url, p);
  }
  return p;
}

/** `null` zolang de lijst laadt (of als `enabled` uit staat), `"error"` als hij niet te laden is. */
export function usePlates(base: string, enabled = true): PlateItem[] | null | "error" {
  const [state, setState] = useState<{ base: string; plates: PlateItem[] | "error" } | null>(null);
  useEffect(() => {
    if (!enabled) return;
    let live = true;
    loadPlates(base).then(
      (plates) => { if (live) setState({ base, plates }); },
      // Eén nieuwe poging; daarna niets tonen in plaats van een lege lijst (dan zou zoeken alles "gemist" melden).
      () => loadPlates(base).then((plates) => { if (live) setState({ base, plates }); }, () => { if (live) setState({ base, plates: "error" }); }),
    );
    return () => { live = false; };
  }, [base, enabled]);
  return enabled && state?.base === base ? state.plates : null;
}
