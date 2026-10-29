"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { messages } from "@/i18n/nl";

/** Een code invullen om mee te doen (ADR 0060). */
export function JoinTogether({ market, href }: { market: string; href: string }) {
  const t = messages(market);
  const [code, setCode] = useState("");
  const [error, setError] = useState(false);
  const router = useRouter();
  const ok = /^[A-HJ-NP-Z]{4}$/.test(code);
  return (
    <form className="kh-together" onSubmit={(e) => { e.preventDefault(); if (ok) router.push(`${href}/${code}`); else setError(true); }}>
      <label className="hint" htmlFor="samen-code">{t.together.codeHint}</label>
      <div className="kh-together-code">
        <input id="samen-code" value={code} maxLength={4} autoComplete="off" autoCapitalize="characters" spellCheck={false} inputMode="text"
          aria-invalid={error && !ok ? true : undefined} onChange={(e) => { setCode(e.target.value.toUpperCase().replace(/[^A-Z]/g, "")); setError(false); }} />
        <button type="submit" className="ui-btn" data-variant="primary">{t.together.join}</button>
      </div>
      {error && !ok && <p className="hint" role="alert">{t.together.codeHint}</p>}
    </form>
  );
}
