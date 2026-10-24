"use client";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo, type CSSProperties } from "react";
import { KIND_GROUP, type PlateItem, type Taxonomy } from "@/lib/types";
import { messages } from "@/i18n/nl";
import { PlateCard } from "./PlateCard";
import { book, useBook } from "@/lib/local";

type Key = "soort" | "onderwerp" | "werelddeel" | "land" | "feestdag" | "leeftijd";

/** Filters en raster. De filterstand staat in de URL, zodat je hem kunt delen en de pagina zelf gecachet blijft. */
export function Browse({ plates, taxonomy, market, language }: { plates: PlateItem[]; taxonomy: Taxonomy; market: string; language: string }) {
  const t = messages(language);
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const picks = useBook();
  const f = {
    kind: params.get("soort") ?? "alle",
    cat: params.get("onderwerp") ?? "alle", cont: params.get("werelddeel") ?? "alle", land: params.get("land") ?? "alle",
    hol: params.get("feestdag") ?? "alle", age: params.get("leeftijd") ?? "alle",
  };
  const set = (changes: Partial<Record<Key, string>>) => {
    const next = new URLSearchParams(params.toString());
    for (const [k, v] of Object.entries(changes)) { if (!v || v === "alle") next.delete(k); else next.set(k, v); }
    const qs = next.toString();
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  };

  const inCat = (p: PlateItem, c: string) => c === "alle" || (c === "wereld" ? !!p.world : c === "feest" ? !!p.holiday : p.category === c);
  const ofKind = (p: PlateItem, k: string) => k === "alle" || KIND_GROUP[p.kind] === k || p.kind === k;
  const aged = plates.filter((p) => (f.age === "alle" || p.age === f.age) && ofKind(p, f.kind));
  const crafts = plates.filter((p) => p.kind !== "kleurplaat").length;
  const groups = new Set(plates.map((p) => KIND_GROUP[p.kind]));
  const kindOptions = ([["alle", t.allKinds], ["kleurplaat", t.kindColoring], ["knutselen", t.kindCrafts], ["leren", t.kindLearn], ["tekenen", t.kindDrawing]] as const)
    .filter(([k]) => k === "alle" || groups.has(k));
  const visible = useMemo(() => aged.filter((p) => inCat(p, f.cat)
    && (f.cat !== "wereld" || f.cont === "alle" || p.world?.continent === f.cont)
    && (f.cat !== "wereld" || f.land === "alle" || p.world?.country === f.land)
    && (f.cat !== "feest" || f.hol === "alle" || p.holiday === f.hol)), [aged, f.cat, f.cont, f.land, f.hol]);

  const cont = taxonomy.continents.find((c) => c.slug === f.cont);
  const lands = cont ? [...new Set(aged.filter((p) => p.world?.continent === cont.slug && p.world.country).map((p) => p.world!.country!))].sort((a, b) => a.localeCompare(b, language)) : [];
  const age = taxonomy.ages.find((a) => a.slug === f.age);
  const chip = (key: Key, value: string, name: string, color: string, n: number, on: boolean, small = false) => (
    <button key={value} type="button" className="chip" style={{ "--c": color } as CSSProperties} aria-pressed={on}
      onClick={() => set(key === "onderwerp" ? { onderwerp: value, werelddeel: "alle", land: "alle", feestdag: "alle" } : key === "werelddeel" ? { werelddeel: value, land: "alle" } : { [key]: value })}>
      <i />{name} <small>{n}</small>{small ? null : null}
    </button>
  );

  return (
    <>
      <div className="filters">
        {crafts > 0 && (
          <div className="frow"><span className="flabel">{t.kind}</span>
            <div className="seg seg-scroll" role="group" aria-label={t.kind}>
              {kindOptions.map(([k, label]) => (
                <button key={k} type="button" aria-pressed={f.kind === k} onClick={() => set({ soort: k })}>{label}</button>
              ))}
            </div>
          </div>
        )}
        <div className="frow"><span className="flabel">{t.topic}</span>
          <nav className="chips" aria-label={t.topic}>
            {chip("onderwerp", "alle", t.all, "var(--color-text)", aged.length, f.cat === "alle")}
            {taxonomy.categories.map((c) => chip("onderwerp", c.slug, c.name, c.color, aged.filter((p) => inCat(p, c.slug)).length, f.cat === c.slug))}
          </nav>
        </div>
        {f.cat === "wereld" && (
          <div className="frow"><span className="flabel">{t.continent}</span>
            <nav className="chips sm" aria-label={t.continent}>
              {chip("werelddeel", "alle", t.wholeWorld, "var(--color-text)", aged.filter((p) => p.world).length, f.cont === "alle")}
              {taxonomy.continents.map((c) => chip("werelddeel", c.slug, c.name, c.color, aged.filter((p) => p.world?.continent === c.slug).length, f.cont === c.slug))}
            </nav>
          </div>
        )}
        {f.cat === "wereld" && cont && lands.length > 0 && (
          <div className="frow"><span className="flabel">{t.country}</span>
            <nav className="chips sm" aria-label={t.country}>
              {chip("land", "alle", t.whole(cont.name), cont.color, aged.filter((p) => p.world?.continent === cont.slug).length, f.land === "alle")}
              {lands.map((l) => chip("land", l, l, cont.color, aged.filter((p) => p.world?.country === l).length, f.land === l))}
            </nav>
          </div>
        )}
        {f.cat === "feest" && (
          <div className="frow"><span className="flabel">{t.holiday}</span>
            <nav className="chips sm" aria-label={t.holiday}>
              {chip("feestdag", "alle", t.allHolidays, "var(--color-text)", aged.filter((p) => p.holiday).length, f.hol === "alle")}
              {taxonomy.holidays.map((h) => chip("feestdag", h.slug, h.name, "var(--krijt-teal)", aged.filter((p) => p.holiday === h.slug).length, f.hol === h.slug))}
            </nav>
          </div>
        )}
        <div className="frow"><span className="flabel">{t.age}</span>
          <div className="seg" role="group" aria-label={t.age}>
            <button type="button" aria-pressed={f.age === "alle"} onClick={() => set({ leeftijd: "alle" })}>{t.allAges}</button>
            {taxonomy.ages.map((a) => (
              <button key={a.slug} type="button" aria-pressed={f.age === a.slug} onClick={() => set({ leeftijd: a.slug })}>
                <span className="lv" aria-hidden="true">{Array.from({ length: Math.max(4, ...taxonomy.ages.map((x) => x.level)) }, (_, i) => i + 1).map((k) => <b key={k} className={k <= a.level ? "on" : ""} />)}</span>{a.name}
              </button>
            ))}
          </div>
          {age?.hint && <p className="hint">{age.hint}</p>}
        </div>
      </div>
      <main className={`grid${picks.picking ? " picking" : ""}`}>
        {visible.length === 0 ? (
          <div className="empty"><b>{t.emptyTitle}</b><span>{t.emptyText}</span>
            <button type="button" className="btn" onClick={() => router.replace(pathname, { scroll: false })}>{t.showAll}</button></div>
        ) : visible.map((p) => (
          <PlateCard key={p.slug} plate={p} market={market} taxonomy={taxonomy} view={f.cat} yr={t.yr} kindLabel={p.kind !== "kleurplaat" ? t.kindNames[p.kind] : undefined}
            {...(picks.picking ? { pick: { selected: picks.slugs.includes(p.slug), onToggle: () => book.toggle(p.slug) } } : {})} />
        ))}
      </main>
    </>
  );
}
