"use client";
import Link from "next/link";
import { messages } from "@/i18n/nl";
import { book, useBook } from "@/lib/local";

/** Knop in de kop: begin of stop met platen kiezen voor een boekje. */
export function BookButton({ language }: { language: string }) {
  const t = messages(language);
  const { picking } = useBook();
  return <button type="button" className="btn" aria-pressed={picking} onClick={() => book.setPicking(!picking)}>{picking ? t.picking : t.makeBook}</button>;
}

/** Balk onderin tijdens het kiezen. */
export function PickBar({ market, language }: { market: string; language: string }) {
  const t = messages(language);
  const { picking, slugs } = useBook();
  if (!picking) return null;
  return (
    <div className="pickbar no-print" role="region" aria-label={t.picked(slugs.length)}>
      <div className="in">
        <div><b aria-live="polite">{t.picked(slugs.length)}</b><p className="hint">{t.pickHint}</p></div>
        <div className="row">
          <button type="button" className="btn" onClick={() => book.setPicking(false)}>{t.stop}</button>
          {slugs.length > 0
            ? <Link className="btn primary" href={`/${market}/boekje?platen=${slugs.join(",")}`}>{t.viewBook}</Link>
            : <button type="button" className="btn primary" disabled>{t.viewBook}</button>}
        </div>
      </div>
    </div>
  );
}
