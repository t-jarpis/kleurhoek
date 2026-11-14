let busyUntil = 0;

/**
 * Opent het printvenster van de browser, maar niet twee keer kort na elkaar (ADR 0020). Op een iPhone of iPad
 * verschijnt het printvenster pas na een tel; wie dan nog eens tikt, vraagt een tweede venster en krijgt van
 * Safari "Onderdruk waarschuwingen". Kies je dat, dan werkt printen op die pagina niet meer tot je hem herlaadt.
 * Daarom telt een tik binnen 5 seconden (of binnen 1 seconde na het sluiten van het venster) niet.
 */
export function openPrint(): boolean {
  const now = Date.now();
  if (now < busyUntil) return false;
  busyUntil = now + 5000;
  const after = () => {
    busyUntil = Math.max(busyUntil, Date.now() + 1000);
    window.removeEventListener("afterprint", after);
  };
  window.addEventListener("afterprint", after);
  window.print();
  return true;
}

/** Alleen voor tests. */
export function resetPrintGuard() { busyUntil = 0; }
