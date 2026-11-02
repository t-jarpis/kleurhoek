"use client";
import { useSyncExternalStore } from "react";

/**
 * Platen in het raster in kleur of als lijnen (ADR 0070, design system: ColorPreview). Standaard in kleur; de keuze
 * blijft op het apparaat (localStorage, geen cookie) en geldt voor elk raster tegelijk. De kleurstudio, het printen
 * en het boekje gebruiken altijd de lijnen.
 */
const KEY = "kh:inkleur";
const listeners = new Set<() => void>();

function read(): boolean {
  try { return localStorage.getItem(KEY) !== "0"; } catch { return true; }
}
function subscribe(fn: () => void) {
  listeners.add(fn);
  const onStorage = (e: StorageEvent) => { if (e.key === KEY) fn(); };
  window.addEventListener("storage", onStorage);
  return () => { listeners.delete(fn); window.removeEventListener("storage", onStorage); };
}
function write(on: boolean) {
  try { localStorage.setItem(KEY, on ? "1" : "0"); } catch { /* niet onthouden: alleen voor nu */ }
  memory = on;
  listeners.forEach((fn) => fn());
}
// Zonder opslag (privévenster) toch kunnen wisselen.
let memory: boolean | null = null;
const snapshot = () => memory ?? read();

export function useColorPreview(): [boolean, (on: boolean) => void] {
  return [useSyncExternalStore(subscribe, snapshot, () => true), write];
}

/** Het ingekleurde bestand naast het gewone: <versie>[.<taal>-<hash>].kleur.svg. */
export const coloredSrc = (svg: string) => svg.replace(/\.svg$/, ".kleur.svg");

export function PlateImage({ src, alt, eager }: { src: string; alt: string; eager: boolean }) {
  const [on] = useColorPreview();
  return <img src={on ? coloredSrc(src) : src} alt={alt} loading={eager ? "eager" : "lazy"} width={200} height={200} />;
}

export function ColorToggle({ label }: { label: string }) {
  const [on, set] = useColorPreview();
  return <button type="button" className="ui-switch" aria-pressed={on} onClick={() => set(!on)}>{label}</button>;
}
