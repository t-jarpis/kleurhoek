"use client";
import type { PlatePage } from "@/lib/types";

/**
 * ExtraPages uit het design system (ADR 0027): pagina 2, 3 … met een eigen printknop. Antwoorden
 * staan apart en ingeklapt. Printen zet alleen dat vel op papier (zie .kh-print-target in globals.css).
 */
export interface ExtraPagesLabels { morePages: string; answers: string; /** Met {n} voor het paginanummer. */ printPage: string }

export function ExtraPages({ pages, labels }: { pages: PlatePage[]; labels: ExtraPagesLabels }) {
  if (!pages.length) return null;
  const extra = pages.filter((p) => p.role === "extra"), answers = pages.filter((p) => p.role === "antwoorden");
  // Eén vel printen: een kopie direct onder <body>; de rest van de pagina doet in print niet mee.
  const print = (el: HTMLElement | null) => {
    if (!el) return;
    const sheet = document.createElement("div");
    sheet.id = "kh-print-sheet";
    sheet.innerHTML = el.innerHTML;
    document.body.appendChild(sheet);
    document.body.dataset.printPage = "1";
    const done = () => { sheet.remove(); delete document.body.dataset.printPage; window.removeEventListener("afterprint", done); };
    window.addEventListener("afterprint", done);
    window.print();
    setTimeout(done, 1000);
  };
  const card = (p: PlatePage) => (
    <figure key={p.number} className="kh-page">
      <div className="kh-page-paper" aria-hidden="true" dangerouslySetInnerHTML={{ __html: p.svg.replace("<svg ", '<svg class="sheet" ') }} />
      <figcaption>{p.title}</figcaption>
      <button type="button" className="btn" onClick={(e) => print(e.currentTarget.closest("figure")?.querySelector<HTMLElement>(".kh-page-paper") ?? null)}>{labels.printPage.replace("{n}", String(p.number))}</button>
    </figure>
  );
  return (
    <div className="extra-pages">
      {extra.length > 0 && <><h3>{labels.morePages}</h3><div className="kh-pages">{extra.map(card)}</div></>}
      {answers.length > 0 && (
        <details className="kh-answers"><summary>{labels.answers}</summary><div className="kh-pages">{answers.map(card)}</div></details>
      )}
    </div>
  );
}
