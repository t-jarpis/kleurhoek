"use client";
import { useSyncExternalStore } from "react";
import { hang, togglePick, type Fills, type FridgeItem } from "./studio";

/**
 * Alles wat op dit apparaat bewaard blijft (koelkast, keuze voor het boekje). Zonder account en
 * zonder server: het werk van een kind hoort bij het apparaat, niet bij ons.
 */
const FRIDGE = "kh:koelkast";
const BOOK = "kh:boekje";
const EVENT = "kh:local";

function read<T>(key: string, fallback: T): T {
  try { const raw = localStorage.getItem(key); return raw ? (JSON.parse(raw) as T) : fallback; } catch { return fallback; }
}
function write(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* opslag vol of geblokkeerd: dan werkt het alleen deze sessie niet */ }
  cache.delete(key);
  window.dispatchEvent(new Event(EVENT));
}

// useSyncExternalStore wil een stabiele waarde zolang er niets verandert.
const cache = new Map<string, unknown>();
function snapshot<T>(key: string, fallback: T): T {
  if (!cache.has(key)) cache.set(key, read(key, fallback));
  return cache.get(key) as T;
}
function subscribe(onChange: () => void) {
  const storage = (e: StorageEvent) => { if (e.key === FRIDGE || e.key === BOOK) { cache.clear(); onChange(); } };
  window.addEventListener(EVENT, onChange);
  window.addEventListener("storage", storage);
  return () => { window.removeEventListener(EVENT, onChange); window.removeEventListener("storage", storage); };
}

const NO_ITEMS: FridgeItem[] = [];
interface BookState { picking: boolean; slugs: string[] }
const NO_BOOK: BookState = { picking: false, slugs: [] };

export function useFridge(): FridgeItem[] {
  return useSyncExternalStore(subscribe, () => snapshot(FRIDGE, NO_ITEMS), () => NO_ITEMS);
}
export function useBook(): BookState {
  return useSyncExternalStore(subscribe, () => snapshot(BOOK, NO_BOOK), () => NO_BOOK);
}

export const fridge = {
  hang(item: { slug: string; version: number; fills: Fills; name: string }, date: string) {
    const id = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
    write(FRIDGE, hang(read(FRIDGE, NO_ITEMS), { ...item, fills: { ...item.fills }, id, date }));
  },
  remove(id: string) { write(FRIDGE, read(FRIDGE, NO_ITEMS).filter((i) => i.id !== id)); },
  /** Verder kleuren: de kleuren van de koelkast worden het werk in de kleurstudio. */
  resume(item: FridgeItem) {
    try { localStorage.setItem(`kh:${item.slug}:v${item.version}`, JSON.stringify({ fills: item.fills, name: item.name })); } catch { /* zie write */ }
  },
};

export const book = {
  setPicking(picking: boolean) { write(BOOK, { ...read(BOOK, NO_BOOK), picking }); },
  toggle(slug: string) { const s = read(BOOK, NO_BOOK); write(BOOK, { ...s, slugs: togglePick(s.slugs, slug) }); },
  set(slugs: string[]) { write(BOOK, { ...read(BOOK, NO_BOOK), slugs }); },
};
