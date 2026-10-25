"use client";
import { useState } from "react";

const TITLE_MAX = 70, DESC_MAX = 170;

function Count({ n, max, id }: { n: number; max: number; id: string }) {
  const over = n > max;
  return <span id={id} className="ui-snippet-count" {...(over ? { "data-over": "" } : {})}>{n} van {max} tekens{over ? ", te lang" : ""}</span>;
}

/** Titel en omschrijving van de voorpagina van één markt, met het voorbeeld in zoekresultaten (SnippetPreview). */
export function SnippetFields({ market, host, title, description }: { market: string; host: string; title: string | null; description: string | null }) {
  const [t, setT] = useState(title ?? "");
  const [d, setD] = useState(description ?? "");
  const key = market.toLowerCase();
  return (
    <div className="stack">
      <input type="hidden" name="market" value={market} />
      <label className="field"><span>Titel</span>
        <input name={`title-${market}`} value={t} onChange={(e) => setT(e.target.value)} maxLength={TITLE_MAX + 20} aria-describedby={`tc-${key}`} placeholder="Kleurhoek" />
        <Count n={t.length} max={TITLE_MAX} id={`tc-${key}`} />
      </label>
      <label className="field"><span>Omschrijving</span>
        <textarea name={`description-${market}`} value={d} onChange={(e) => setD(e.target.value)} rows={3} maxLength={DESC_MAX + 40} aria-describedby={`dc-${key}`} placeholder="Leeg: de vaste introductietekst van de site" />
        <Count n={d.length} max={DESC_MAX} id={`dc-${key}`} />
      </label>
      <figure className="ui-snippet" style={{ margin: 0 }}>
        <figcaption className="visually-hidden">Voorbeeld in zoekresultaten</figcaption>
        <p className="ui-snippet-url">{host} › {key}</p>
        <p className="ui-snippet-title">{t || "Kleurhoek"}</p>
        <p className="ui-snippet-desc">{d || "Eigen kleurplaten om online in te kleuren of te printen."}</p>
      </figure>
    </div>
  );
}
