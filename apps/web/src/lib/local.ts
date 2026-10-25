"use client";
import { useSyncExternalStore } from "react";
import { hang, togglePick, type Fills, type FridgeItem } from "./studio";

/**
 * Alles wat op dit apparaat bewaard blijft (koelkast, keuze voor het boekje, favorieten). Koelkast en boekje
 * zonder server: het werk van een kind hoort bij het apparaat, niet bij ons. Favorieten gaan met een account mee
 * naar elk apparaat (ADR 0039).
 */
const FRIDGE = "kh:koelkast";
const BOOK = "kh:boekje";
const FAVS = "kh:favorieten";
/** Staan de favorieten op dit apparaat gelijk met een account? Dan gaat elke wijziging ook naar het account. */
const FAVS_ACCOUNT = "kh:favorieten:account";
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
  const storage = (e: StorageEvent) => { if (e.key === FRIDGE || e.key === BOOK || e.key === FAVS) { cache.clear(); onChange(); } };
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

// ---------- Favorieten (ADR 0039) ----------
// Zonder account op het apparaat. Met een account: na inloggen één keer samenvoegen, daarna is het account leidend,
// zodat iets wat op een ander apparaat is weggehaald niet terugkomt.

const NO_FAVS: string[] = [];
export function useFavorites(): string[] {
  return useSyncExternalStore(subscribe, () => snapshot(FAVS, NO_FAVS), () => NO_FAVS);
}

let syncing: Promise<boolean> | null = null;
export const favorites = {
  /** Eén keer per pagina: gelijkzetten met het account als iemand is ingelogd. Geeft terug of dat zo is. */
  sync(): Promise<boolean> {
    syncing ??= (async () => {
      const res = await fetch("/auth/favorites").catch(() => null);
      if (!res?.ok) { if (read(FAVS_ACCOUNT, false)) write(FAVS_ACCOUNT, false); return false; }
      let server = ((await res.json()) as { slugs: string[] }).slugs;
      const wasLinked = read(FAVS_ACCOUNT, false);
      const extra = wasLinked ? [] : read(FAVS, NO_FAVS).filter((s) => !server.includes(s));
      if (extra.length) {
        const merged = await fetch("/auth/favorites", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ slugs: extra }) }).catch(() => null);
        if (merged?.ok) server = ((await merged.json()) as { slugs: string[] }).slugs;
      }
      write(FAVS, server);
      if (!wasLinked) write(FAVS_ACCOUNT, true);
      return true;
    })();
    return syncing;
  },
  /** Aan of uit. Geeft de nieuwe stand. */
  toggle(slug: string): boolean {
    const list = read(FAVS, NO_FAVS);
    const on = !list.includes(slug);
    write(FAVS, on ? [...list, slug] : list.filter((s) => s !== slug));
    if (read(FAVS_ACCOUNT, false)) void fetch(`/auth/favorites/${slug}`, { method: on ? "PUT" : "DELETE" }).catch(() => undefined);
    return on;
  },
};
