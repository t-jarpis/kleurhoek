import { useEffect, useRef, useState } from "react";

let busyUntil = 0;

/**
 * Opent het printvenster van de browser, maar niet twee keer kort na elkaar (ADR 0020). Op een iPhone of iPad
 * verschijnt het printvenster pas na een tel; wie dan nog eens tikt, vraagt een tweede venster en krijgt van
 * Safari "Onderdruk waarschuwingen". Kies je dat, dan werkt printen op die pagina niet meer tot je hem herlaadt.
 * Daarom telt een tik binnen 5 seconden (of binnen 1 seconde na het sluiten van het venster) niet; `usePrint`
 * laat de knop zo lang "bezig" zien (design system: Button › Bezig).
 */
export function openPrint(before?: () => void): boolean {
  const now = Date.now();
  if (now < busyUntil) return false;
  busyUntil = now + 5000;
  const after = () => {
    busyUntil = Math.max(busyUntil, Date.now() + 1000);
    window.removeEventListener("afterprint", after);
  };
  window.addEventListener("afterprint", after);
  before?.(); // vóór window.print: daar komt beforeprint al uit (zie trackPrint)
  window.print();
  return true;
}

/**
 * Printknop met bezig-stand: `busy` is waar zolang een nieuwe tik niets doet. Zet op de knop
 * `aria-busy={busy}` en `aria-disabled={busy}` en toon de tekst met "…".
 */
export function usePrint(onPrint?: () => void) {
  const [busy, setBusy] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  const print = () => {
    if (!openPrint(onPrint)) return false;
    setBusy(true);
    const wait = () => {
      const left = busyUntil - Date.now();
      if (left > 0) timer.current = setTimeout(wait, left);
      else setBusy(false);
    };
    wait();
    return true;
  };
  return { busy, print };
}

/** Alleen voor tests. */
export function resetPrintGuard() { busyUntil = 0; }
