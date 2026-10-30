"use client";
import { useEffect, useState } from "react";

/** Kopiëren en de deelknop van de telefoon, voor teksten die Thijs zelf deelt (ADR 0063). */
export function ShareButtons({ text, title }: { text: string; title: string }) {
  const [copied, setCopied] = useState(false);
  // Pas na het laden: de server kent navigator niet, anders verschilt de eerste weergave.
  const [canShare, setCanShare] = useState(false);
  useEffect(() => setCanShare("share" in navigator), []);
  return (
    <>
      <button type="button" className="ui-btn" onClick={() => void navigator.clipboard.writeText(text).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000); })}>{copied ? "Gekopieerd" : "Kopiëren"}</button>
      {canShare && <button type="button" className="ui-btn" onClick={() => void navigator.share({ title, text }).catch(() => undefined)}>Delen…</button>}
    </>
  );
}
