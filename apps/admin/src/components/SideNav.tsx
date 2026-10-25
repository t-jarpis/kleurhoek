"use client";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

/**
 * Zijmenu (design system: AdminNav). Op een breed scherm altijd zichtbaar; op een telefoon een balk met het merk
 * en een knop Menu die de lijst opent. Na het kiezen van een pagina gaat het menu weer dicht.
 */
export function SideNav({ brand, children }: { brand: ReactNode; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const path = usePathname();
  useEffect(() => {
    setOpen(false);
    // Tabbladen die horizontaal schuiven: het actieve tabblad in beeld (op een telefoon valt het anders buiten de rand).
    document.querySelectorAll<HTMLElement>(".tabs [aria-current='page']").forEach((el) => el.scrollIntoView({ block: "nearest", inline: "center" }));
    // Vervagen aan de rand alleen als er echt meer is om naartoe te schuiven (data-more, zie globals.css).
    const tabs = [...document.querySelectorAll<HTMLElement>(".tabs")];
    const mark = () => tabs.forEach((t) => { if (t.scrollWidth - t.clientWidth - t.scrollLeft > 4) t.dataset.more = ""; else delete t.dataset.more; });
    mark();
    tabs.forEach((t) => t.addEventListener("scroll", mark, { passive: true }));
    window.addEventListener("resize", mark);
    return () => { tabs.forEach((t) => t.removeEventListener("scroll", mark)); window.removeEventListener("resize", mark); };
  }, [path]);
  useEffect(() => {
    if (!open) return;
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [open]);
  return (
    <nav className="side" aria-label="Beheer" data-open={open || undefined}>
      <div className="side-top">
        <div className="brand">{brand}</div>
        <button type="button" className="ghost side-toggle" aria-expanded={open} aria-controls="side-items" onClick={() => setOpen((o) => !o)}>
          <svg className="ui-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" aria-hidden="true">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
          {open ? "Sluiten" : "Menu"}
        </button>
      </div>
      <div className="side-items" id="side-items">{children}</div>
    </nav>
  );
}
