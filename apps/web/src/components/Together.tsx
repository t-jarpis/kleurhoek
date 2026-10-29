"use client";
import { Icon } from "@kleurhoek/theme";
import { useCallback, useEffect, useRef, useState } from "react";
import type { Messages } from "@/i18n/nl";
import type { SharedOp } from "@/lib/atelier";

/**
 * Samen kleuren (ADR 0060): een kamer met een code van vier letters. Dit apparaat stuurt zijn eigen handelingen
 * en vraagt steeds wat er nieuw is (long polling: werkt achter elke proxy en zonder blijvende verbinding).
 * De kamer blijft bestaan zolang iemand kleurt; een half uur niemand, dan stopt hij vanzelf.
 */
export type TogetherStatus = "uit" | "bezig" | "live" | "offline" | "weg";

const clientId = () => Array.from(crypto.getRandomValues(new Uint8Array(6)), (b) => (b % 36).toString(36)).join("") + Date.now().toString(36).slice(-4);
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export function useTogether({ onLog }: { onLog: (confirmed: SharedOp[], pending: SharedOp[]) => void }) {
  const [code, setCode] = useState<string | null>(null);
  const [status, setStatus] = useState<TogetherStatus>("uit");
  const [others, setOthers] = useState(0);
  const client = useRef<string>("");
  const counter = useRef(0);
  const confirmed = useRef<SharedOp[]>([]);
  const pending = useRef<SharedOp[]>([]);
  const queue = useRef<SharedOp[]>([]);
  const abort = useRef<AbortController | null>(null);
  const flushing = useRef(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onLogRef = useRef(onLog);
  onLogRef.current = onLog;

  const publish = () => {
    const seen = new Set(confirmed.current.map((o) => o.id));
    pending.current = pending.current.filter((o) => !seen.has(o.id));
    onLogRef.current(confirmed.current, pending.current);
  };

  const flush = useCallback(async (room: string) => {
    if (flushing.current || !queue.current.length) return;
    flushing.current = true;
    while (queue.current.length) {
      const batch = queue.current.slice(0, 40);
      const res = await fetch(`/v1/together/rooms/${room}/ops`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ client: client.current, ops: batch }) }).catch(() => null);
      if (res?.ok) queue.current = queue.current.slice(batch.length);
      else if (res?.status === 404) { setStatus("weg"); break; }
      else if (res?.status === 400) { queue.current = queue.current.slice(batch.length); }
      else { setStatus("offline"); await sleep(1500); }
    }
    flushing.current = false;
  }, []);

  const loop = useCallback(async (room: string, signal: AbortSignal) => {
    let after = 0;
    let first = true;
    while (!signal.aborted) {
      try {
        const res = await fetch(`/v1/together/rooms/${room}/ops?client=${client.current}&after=${after}${first ? "&wait=0" : ""}`, { signal, cache: "no-store" });
        if (res.status === 404) { setStatus("weg"); return; }
        if (!res.ok) throw new Error(String(res.status));
        const data = await res.json() as { ops: { op: SharedOp }[]; others: number; last: number };
        setStatus("live"); setOthers(data.others);
        if (data.ops.length) {
          const known = new Set(confirmed.current.map((o) => o.id));
          confirmed.current = [...confirmed.current, ...data.ops.map((o) => o.op).filter((o) => !known.has(o.id))];
          publish();
        }
        after = data.last; first = false;
      } catch {
        if (signal.aborted) return;
        setStatus("offline");
        await sleep(2000);
      }
    }
  }, []);

  const begin = (room: string) => {
    abort.current?.abort();
    const ctl = new AbortController();
    abort.current = ctl;
    setCode(room);
    void loop(room, ctl.signal);
  };

  /** Een nieuwe kamer voor deze plaat, met het werk dat er al is. */
  const start = async (market: string, slug: string, version: number, initial: (id: () => string) => SharedOp[]) => {
    setStatus("bezig");
    client.current = clientId(); counter.current = 0; confirmed.current = []; pending.current = []; queue.current = [];
    const res = await fetch("/v1/together/rooms", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ market, slug, version }) }).catch(() => null);
    if (!res?.ok) { setStatus("offline"); setTimeout(() => setStatus("uit"), 2500); return; }
    const { code: room } = await res.json() as { code: string };
    const ops = initial(nextId);
    pending.current = ops; queue.current = [...ops];
    publish();
    begin(room);
    void flush(room);
  };

  /** Meedoen met een bestaande kamer: de plaat van de kamer vervangt wat hier stond. */
  const join = (room: string) => {
    setStatus("bezig");
    client.current = clientId(); counter.current = 0; confirmed.current = []; pending.current = []; queue.current = [];
    publish();
    begin(room.toUpperCase());
  };

  const nextId = () => `${client.current}:${++counter.current}`;

  /** Een eigen handeling: meteen zichtbaar, en zo snel mogelijk naar de kamer. */
  const emit = (op: SharedOp extends infer T ? (T extends { id: string } ? Omit<T, "id"> : never) : never) => {
    if (!code) return;
    const full = { ...op, id: nextId() } as SharedOp;
    pending.current = [...pending.current, full];
    queue.current.push(full);
    publish();
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => void flush(code), 120);
  };

  const stop = () => { abort.current?.abort(); abort.current = null; setCode(null); setStatus("uit"); setOthers(0); };
  useEffect(() => () => abort.current?.abort(), []);

  return { code, status, others, start, join, emit, stop, mine: (id: string | undefined) => !!id && id.startsWith(`${client.current}:`), active: code !== null && status !== "weg" };
}

/** Het paneel in de gereedschapskolom. */
export function TogetherPanel({ t, together, onStart, joinHref }: { t: Messages; together: ReturnType<typeof useTogether>; onStart: () => void; joinHref: string }) {
  const [copied, setCopied] = useState(false);
  const { code, status, others } = together;
  const link = code && typeof window !== "undefined" ? `${window.location.origin}${joinHref}/${code}` : "";
  return (
    <div className="tool kh-together">
      <h2>{t.together.title}</h2>
      {!code ? (
        <>
          <button type="button" className="btn" onClick={onStart} disabled={status === "bezig"}><Icon name="together" size={18} /> {t.together.start}</button>
          <a className="hint" href={joinHref}>{t.together.join}</a>
        </>
      ) : status === "weg" ? (
        <>
          <p className="hint" role="status">{t.together.notFound}</p>
          <button type="button" className="btn" onClick={together.stop}>{t.together.stop}</button>
        </>
      ) : (
        <>
          <p className="hint">{t.together.share}</p>
          <div className="kh-together-code">
            <output aria-label={t.together.code}>{code}</output>
            <button type="button" className="ui-btn" onClick={() => { void navigator.clipboard?.writeText(link).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); }); }}>
              {copied ? t.together.copied : t.together.copyLink}
            </button>
          </div>
          <span className="kh-together-status" data-live={status === "live" && others > 0 ? "" : undefined} role="status">
            {status === "offline" ? t.together.offline : others > 0 ? t.together.others(others) : t.together.waiting}
          </span>
          <p className="hint">{t.together.expires}</p>
          <button type="button" className="btn" onClick={together.stop}>{t.together.stop}</button>
        </>
      )}
    </div>
  );
}
