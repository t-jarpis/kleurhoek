"use client";
import { useEffect, useState } from "react";
import type { PowChallenge } from "@/app/[org]/[market]/contact/actions";

/** Zoekt het getal bij de opgave: sha256(salt + n) = challenge. In stukjes, zodat de pagina blijft reageren. */
export async function solvePow(c: PowChallenge): Promise<number | null> {
  const enc = new TextEncoder();
  for (let n = 0; n <= c.max; n++) {
    const hash = new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(`${c.salt}${n}`)));
    let hex = "";
    for (const b of hash) hex += b.toString(16).padStart(2, "0");
    if (hex === c.challenge) return n;
    if (n % 2000 === 0) await new Promise((r) => setTimeout(r, 0));
  }
  return null;
}

/**
 * Onzichtbare rekenpuzzel (ADR 0048): haalt een opgave op en lost die op de achtergrond op. Geeft de oplossing
 * als JSON voor een verborgen veld. Een nieuwe `reset` (bijvoorbeeld na een foutmelding) geeft een nieuwe opgave,
 * want elke oplossing is één keer bruikbaar.
 */
export function usePow(challenge: () => Promise<PowChallenge | null>, reset: unknown): string {
  const [pow, setPow] = useState("");
  useEffect(() => {
    let stop = false;
    setPow("");
    void (async () => {
      const c = await challenge().catch(() => null);
      if (!c || stop || !globalThis.crypto?.subtle) return;
      const number = await solvePow(c);
      if (number !== null && !stop) setPow(JSON.stringify({ challenge: c.challenge, salt: c.salt, number, expires: c.expires, signature: c.signature }));
    })();
    return () => { stop = true; };
  }, [challenge, reset]);
  return pow;
}
