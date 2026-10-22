"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { messages } from "@/i18n/nl";
import { book } from "@/lib/local";
import { track } from "@/lib/track";
import type { PlateDetail } from "@/lib/types";
import { Sheet, sheetPlate } from "./Sheet";

export interface BookPlate { plate: PlateDetail; inner: string; ageWidth: number; foot: string }

const OWNER = "kh:boekje-naam";

function star(cx: number, cy: number, outer: number, inner: number) {
  const pts = Array.from({ length: 10 }, (_, i) => {
    const a = -Math.PI / 2 + (i * Math.PI) / 5, r = i % 2 ? inner : outer;
    return `${(cx + r * Math.cos(a)).toFixed(1)} ${(cy + r * Math.sin(a)).toFixed(1)}`;
  });
  return `M${pts.join(" L")}Z`;
}

/** Voorblad met de naam van het kind en Oki en Sjors. Ook in te kleuren. */
function Cover({ owner, count, mascots, t }: { owner: string; count: number; mascots: (string | null)[]; t: ReturnType<typeof messages> }) {
  const size = owner ? Math.min(30, 300 / Math.max(owner.length + 4, 6)) : 0;
  const [uil, slak] = mascots;
  return (
    <svg className="sheet" viewBox="0 0 200 270" style={{ "--sw": 2.4 } as React.CSSProperties} role="img" aria-label={t.cover}>
      <rect x={8} y={8} width={184} height={254} rx={12} fill="none" stroke="#1d1b22" strokeWidth={2.4} />
      <path className="r" d={star(30, 32, 10, 4)} /><path className="r" d={star(172, 36, 8, 3.5)} /><path className="r" d={star(166, 128, 7, 3)} />
      <text className="r nm" x={100} y={70} textAnchor="middle" fontSize={21}>{t.myBook}</text>
      {owner && <text className="r nm" x={100} y={108} textAnchor="middle" fontSize={size}>{t.of} {owner}</text>}
      <clipPath id="cover-frame"><rect x={10} y={10} width={180} height={250} rx={11} /></clipPath>
      <g clipPath="url(#cover-frame)">
        {uil && <g transform="translate(12 116) scale(.6)" dangerouslySetInnerHTML={{ __html: uil }} />}
        {slak && <g transform="translate(98 142) scale(.48)" dangerouslySetInnerHTML={{ __html: slak }} />}
      </g>
      <text x={100} y={254} textAnchor="middle" fontSize={8} fill="#5d6672" fontFamily="var(--f-body)">{t.bookCount(count)}</text>
    </svg>
  );
}

export function Booklet({ market, language, items, mascots, title }: { market: string; language: string; items: BookPlate[]; mascots: (string | null)[]; title: string }) {
  const t = messages(language);
  const router = useRouter();
  const [owner, setOwner] = useState("");
  const [numbers, setNumbers] = useState(false);
  const [learn, setLearn] = useState(false);
  const slugs = items.map((i) => i.plate.slug);

  // De URL is leidend; de keuze op de homepagina loopt mee, zodat verder kiezen gewoon werkt.
  useEffect(() => { book.set(slugs); }, [slugs.join(",")]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { try { setOwner(localStorage.getItem(OWNER) ?? ""); } catch { /* geen opslag */ } }, []);
  const changeOwner = (v: string) => { setOwner(v); try { localStorage.setItem(OWNER, v); } catch { /* geen opslag */ } };

  const remove = (slug: string) => {
    const next = slugs.filter((s) => s !== slug);
    book.set(next);
    router.replace(next.length ? `/${market}/boekje?platen=${next.join(",")}` : `/${market}/boekje`, { scroll: false });
  };

  return (
    <div className="wrap">
      <div className="book">
        <div className="studio-top no-print">
          <Link href={`/${market}`} className="btn" onClick={() => book.setPicking(true)}>{t.backToPicking}</Link>
          <h1>{title}</h1>
        </div>
        <aside className="tools no-print">
          <div className="tool">
            <h2>{t.cover}</h2>
            <label className="hint" htmlFor="owner">{t.bookOwner}</label>
            <input id="owner" className="input" maxLength={16} placeholder={t.bookOwnerPlaceholder} autoComplete="off" value={owner} onChange={(e) => changeOwner(e.target.value)} />
          </div>
          <div className="tool">
            <h2>{t.sheetKind}</h2>
            <label className="chk"><input type="checkbox" checked={numbers} onChange={(e) => setNumbers(e.target.checked)} /> <span>{t.bookNumbers}</span></label>
            <label className="chk"><input type="checkbox" checked={learn} onChange={(e) => setLearn(e.target.checked)} /> <span>{t.bookLearn}</span></label>
          </div>
          <p className="hint">{items.length ? t.bookInfo(items.length) : t.bookEmpty}</p>
          <button type="button" className="btn primary" disabled={!items.length}
            onClick={() => { track({ type: "print", market }); window.print(); }}>{t.printBook}</button>
        </aside>
        <div className="sheets">
          <div className="a4 cover"><Cover owner={owner} count={items.length} mascots={mascots} t={t} /><span className="pg">{t.cover}</span></div>
          {items.map(({ plate, inner, ageWidth, foot }, k) => (
            <div className="a4" key={plate.slug}>
              <button type="button" className="x no-print" aria-label={t.remove(plate.name)} onClick={() => remove(plate.slug)}>×</button>
              <h3>{plate.name}</h3>
              <Sheet plate={sheetPlate(plate)} inner={inner} sw={ageWidth} numbers={numbers} legend={numbers} learn={learn} />
              <span className="pg">{t.page(k + 1)}</span>
              <span className="foot">{foot}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
