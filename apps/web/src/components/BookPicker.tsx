"use client";
import { useHref } from "./Base";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Icon } from "@kleurhoek/theme";
import { messages } from "@/i18n/nl";
import { book, useBook } from "@/lib/local";
import type { PlateItem } from "@/lib/types";
import { PlateImage } from "./ColorPreview";

/** Knop in de kop: begin of stop met platen kiezen voor een boekje. */
export function BookButton({ language }: { language: string }) {
  const t = messages(language);
  const { picking } = useBook();
  return <button type="button" className="btn" aria-pressed={picking} onClick={() => book.setPicking(!picking)}>{picking ? t.picking : t.makeBook}</button>;
}

/**
 * Balk onderin (ADR 0076): tijdens het kiezen, en daarna zolang er iets in het boekje staat, op elke pagina
 * behalve het boekje zelf. Er komt alleen een balk als iemand zelf iets in het boekje heeft gezet.
 */
export function PickBar({ language }: { language: string }) {
  const href = useHref();
  const path = usePathname();
  const t = messages(language);
  const { picking, slugs } = useBook();
  const [sure, setSure] = useState(false);
  if (/\/boekje\/?$/.test(path ?? "") || (!picking && !slugs.length)) return null;
  const view = slugs.length > 0
    ? <Link className="btn primary" href={href(`/boekje?platen=${slugs.join(",")}`)}>{picking ? t.viewBook : t.bookOpen}</Link>
    : <button type="button" className="btn primary" disabled>{t.viewBook}</button>;
  return (
    <>
      <div className="pickbar-space no-print" aria-hidden="true" />
      <div className="pickbar no-print" role="region" aria-label={picking ? t.picked(slugs.length) : t.bookBar(slugs.length)}>
        <div className="in">
          {picking
            ? <div><b aria-live="polite">{t.picked(slugs.length)}</b><p className="hint">{t.pickHint}</p></div>
            : <b aria-live="polite">{t.bookBar(slugs.length)}</b>}
          <div className="row">
            {picking
              ? <button type="button" className="btn" onClick={() => book.setPicking(false)}>{t.stop}</button>
              : <button type="button" className="btn" onClick={() => { if (sure) { book.set([]); setSure(false); } else setSure(true); }} onBlur={() => setSure(false)}>{sure ? t.bookClearSure : t.bookClear}</button>}
            {view}
          </div>
        </div>
      </div>
    </>
  );
}

/** Een plaat in of uit het boekje zetten, vanaf de plaat zelf (ADR 0076). */
export function BookToggle({ slug, language }: { slug: string; language: string }) {
  const t = messages(language);
  const { slugs } = useBook();
  const on = slugs.includes(slug);
  return <button type="button" className="btn" aria-pressed={on} onClick={() => book.toggle(slug)}><Icon name="book" size={16} /> {on ? t.inBookOn : t.inBook}</button>;
}

/**
 * "Nog eentje erbij?" (ADR 0076): na een tik op Printen, één keer, onder de printknop. Drie passende platen om aan te
 * tikken; samen printen opent het boekje met alleen die platen, zonder voorblad en zonder het eigen boekje te wijzigen.
 */
export function MoreToPrint({ plates, language }: { plates: PlateItem[]; language: string }) {
  const href = useHref();
  const t = messages(language);
  const [chosen, setChosen] = useState<string[]>([]);
  if (!plates.length) return null;
  const toggle = (slug: string) => setChosen((c) => (c.includes(slug) ? c.filter((s) => s !== slug) : [...c, slug]));
  return (
    <div className="kh-moreprint no-print" role="region" aria-labelledby="more-title">
      <h2 id="more-title">{t.moreTitle}</h2>
      <p className="hint">{t.moreHint}</p>
      <div className="kh-moreprint-list">
        {plates.map((p) => (
          <button key={p.slug} type="button" aria-pressed={chosen.includes(p.slug)} onClick={() => toggle(p.slug)}>
            {chosen.includes(p.slug) && <span className="tick" aria-hidden="true">✓</span>}
            <span className="paper"><PlateImage src={p.svg} alt="" eager={false} /></span>
            {p.name}
          </button>
        ))}
      </div>
      {chosen.length > 0
        ? <Link className="ui-btn" data-variant="primary" href={href(`/boekje?platen=${chosen.join(",")}&los=1`)}>{t.morePrint(chosen.length)}</Link>
        : <button type="button" className="ui-btn" data-variant="primary" disabled>{t.morePrint(0)}</button>}
    </div>
  );
}
