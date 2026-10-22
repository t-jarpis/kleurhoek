import type { PlateItem, Season, Taxonomy } from "@/lib/types";
import type { Messages } from "@/i18n/nl";
import { PlateCard } from "./PlateCard";

/** Scheurkalender met de feestdagen en het seizoen van nu, en de platen die erbij horen. */
export function SeasonBand({ season, plates, taxonomy, market, t }: { season: Season; plates: PlateItem[]; taxonomy: Taxonomy; market: string; t: Messages }) {
  if (!season.active.length && !season.soon.length) return null;
  const [y, m, d] = season.today.split("-").map(Number) as [number, number, number];
  const weekday = t.weekdays[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
  const label = (x: { date?: string; approximate?: boolean; label?: string | null }) => {
    if (x.label) return x.label;
    if (!x.date) return "";
    const [, mm, dd] = x.date.split("-").map(Number) as [number, number, number];
    return `${x.approximate ? `${t.around} ` : ""}${dd} ${t.months[mm - 1]}`;
  };
  const names = season.active.map((a) => a.name);
  const title = names.length > 1 ? `${names.slice(0, -1).join(", ")} en ${names.at(-1)}` : names[0] ?? t.almostParty;
  const holidays = season.active.filter((a) => a.kind === "holiday");
  const bySlug = new Map(plates.map((p) => [p.slug, p]));
  return (
    <section className="season" aria-label={t.seasonNow}>
      <div className="tear" aria-hidden="true"><span className="tm">{t.months[m - 1]!.slice(0, 3)}</span><b>{d}</b><span className="td">{weekday}</span></div>
      <div className="season-txt">
        <p className="eyebrow">{t.seasonNow}</p>
        <h2>{title}</h2>
        {holidays.length > 0 && <p className="soon">{holidays.map((h, i) => <span key={h.slug}>{i > 0 && " · "}<b>{h.name}</b> ({label(h)})</span>)}</p>}
        {season.soon.length > 0 && <p className="soon">{t.soon}: {season.soon.map((h, i) => <span key={h.slug}>{i > 0 && " · "}<b>{h.name}</b> ({label(h)})</span>)}</p>}
        <div className="minis">
          {season.plates.map((s) => bySlug.get(s)).filter((p): p is PlateItem => !!p).map((p) => <PlateCard key={p.slug} plate={p} market={market} taxonomy={taxonomy} mini yr={t.yr} />)}
        </div>
      </div>
    </section>
  );
}
