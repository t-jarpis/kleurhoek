"use client";
import { useHref } from "./Base";
import { useRouter } from "next/navigation";
import { useEffect, useState, type CSSProperties } from "react";
import { messages } from "@/i18n/nl";
import { fridge, useFridge } from "@/lib/local";
import { svgHeight, svgInner } from "@/lib/svg";
import type { PlateItem } from "@/lib/types";
import { Sheet } from "./Sheet";

const MAGNETS = ["var(--krijt-rood)", "var(--krijt-blauw)", "var(--krijt-geel)", "var(--krijt-groen)", "var(--krijt-roze)", "var(--krijt-oranje)"];
const TILT = [-3, 2, -1.5, 3, -2, 1];
type Loaded = { inner: string; height: number };
const svgCache = new Map<string, Promise<Loaded>>();
const loadInner = (url: string) => {
  if (!svgCache.has(url)) svgCache.set(url, fetch(url).then((r) => (r.ok ? r.text() : "")).then((svg) => ({ inner: svgInner(svg), height: svgHeight(svg) })).catch(() => ({ inner: "", height: 200 })));
  return svgCache.get(url)!;
};

/** De koelkastdeur: eigen werk dat op dit apparaat is opgehangen. Niets gaat naar de server. */
export function Fridge({ market, plates, language }: { market: string; plates: PlateItem[]; language: string }) {
  const href = useHref();
  const t = messages(language);
  const items = useFridge();
  const router = useRouter();
  const [inner, setInner] = useState<Record<string, Loaded>>({});
  const [sure, setSure] = useState<string | null>(null);
  const names = new Map(plates.map((p) => [p.slug, p.name]));
  // Het adres uit de lijst is in de taal van de markt (ADR 0029); een oudere versie valt terug op de brontaal.
  const svgs = new Map(plates.map((p) => [p.slug, p.svg]));
  const pathOf = (i: { slug: string; version: number }) => {
    const current = svgs.get(i.slug);
    return current?.startsWith(`/v1/assets/plates/${i.slug}/${i.version}.`) ? current : `/v1/assets/plates/${i.slug}/${i.version}.svg`;
  };
  const shown = items.filter((i) => names.has(i.slug));

  useEffect(() => {
    let live = true;
    for (const i of shown) {
      const url = pathOf(i);
      if (inner[url] === undefined) void loadInner(url).then((svg) => { if (live) setInner((m) => ({ ...m, [url]: svg })); });
    }
    return () => { live = false; };
  }, [shown, inner]);

  if (!shown.length) return null;
  return (
    <section className="fridge-wrap no-print" aria-label={t.fridge}>
      <h2 className="sec">{t.fridge}</h2>
      <p>{t.fridgeText}</p>
      <div className="fridge">
        {shown.map((item, k) => {
          const name = names.get(item.slug)!;
          const svg = inner[pathOf(item)];
          return (
            <div className="magw" key={item.id}>
              <button type="button" className="mag" style={{ "--rot": `${TILT[k % 6]}deg`, "--mc": MAGNETS[k % 6] } as CSSProperties}
                aria-label={name} onClick={() => { fridge.resume(item); router.push(href(`/platen/${item.slug}`)); }}>
                {svg?.inner ? <Sheet plate={{ name, height: svg.height, regionCount: -1, word: null, countQuestion: null, labels: [], palette: [] }} inner={svg.inner} fills={item.fills} name={item.name} sw={2} marked={false} /> : <span className="mag-empty" />}
              </button>
              <small>
                <span>{name} · {item.date}</span>
                <button type="button" className="linkbtn" onClick={() => {
                  if (sure === item.id) { fridge.remove(item.id); setSure(null); } else { setSure(item.id); setTimeout(() => setSure((s) => (s === item.id ? null : s)), 2500); }
                }}>{sure === item.id ? t.takeOffSure : t.takeOff}</button>
              </small>
            </div>
          );
        })}
      </div>
    </section>
  );
}
