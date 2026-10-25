"use client";
import { useEffect, useState } from "react";
import { messages } from "@/i18n/nl";
import { browserLanguages } from "@/lib/sites";
import { useSites } from "./Base";

const DISMISSED = "kh:taalbanner";

/** Het pad binnen de markt (zonder voorvoegsel), pas na het laden bekend; tot dan de beginpagina. */
function useRest() {
  const { base } = useSites();
  const [rest, setRest] = useState("");
  useEffect(() => {
    const p = window.location.pathname;
    const r = base && (p === base || p.startsWith(`${base}/`)) ? p.slice(base.length) : base ? "" : p === "/" ? "" : p;
    setRest(r + window.location.search);
  }, [base]);
  return rest;
}

/** Taalkeuze onderaan (ADR 0040): elke live markt, naar dezelfde pagina daar. */
export function MarketLinks({ label }: { label: string }) {
  const { market, sites } = useSites();
  const rest = useRest();
  if (sites.length < 2) return null;
  return (
    <nav className="ui-markets" aria-label={label}>
      {sites.map((s) => s.market === market
        ? <span key={s.market} aria-current="true" lang={s.market}>{s.label}</span>
        : <a key={s.market} href={s.root + rest || "/"} lang={s.market} hrefLang={s.market}>{s.label}</a>)}
    </nav>
  );
}

/**
 * Taalbanner (ADR 0040): spreekt de browser een andere taal die we ook hebben, dan een rustige hint in die taal.
 * Nooit automatisch doorsturen. Sluiten wordt op het apparaat onthouden.
 */
export function LangHint() {
  const { market, sites } = useSites();
  const rest = useRest();
  const [target, setTarget] = useState<{ root: string; language: string } | null>(null);
  useEffect(() => {
    try { if (localStorage.getItem(DISMISSED)) return; } catch { /* geen opslag: gewoon tonen */ }
    const lang = browserLanguages(navigator.languages?.join(",") || navigator.language)[0];
    if (!lang || market.startsWith(`${lang}-`)) return;
    const country = market.slice(3);
    const hit = sites.find((s) => s.market === `${lang}-${country}`) ?? sites.find((s) => s.market.startsWith(`${lang}-`));
    if (hit) setTarget({ root: hit.root, language: lang });
  }, [market, sites]);
  if (!target) return null;
  const t = messages(target.language);
  const close = () => { try { localStorage.setItem(DISMISSED, "1"); } catch { /* niet onthouden */ } setTarget(null); };
  return (
    <div className="ui-lang-hint no-print" role="region" aria-label={t.marketsLabel} lang={target.language}>
      <p>{t.langHint}</p>
      <a className="btn" href={target.root + rest || "/"}>{t.langRead}</a>
      <button type="button" className="ui-lang-hint-close" aria-label={t.close} onClick={close}>×</button>
    </div>
  );
}
