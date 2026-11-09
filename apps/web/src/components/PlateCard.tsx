import Link from "next/link";
import type { CSSProperties } from "react";
import type { PlateItem, Taxonomy } from "@/lib/types";
import { link } from "@/lib/sites";
import { cardOf, type CardData } from "@/lib/cards";
import { PlateImage } from "./ColorPreview";

/**
 * Een plaat in het raster. Normaal een link naar de kleurstudio; tijdens het kiezen voor een boekje
 * een knop die de plaat aan- of uitzet.
 */
export function PlateCard({ plate, base, taxonomy, view = "alle", mini = false, eager = mini, yr, pick, kindLabel, alt }: {
  plate: PlateItem; base: string; taxonomy: Taxonomy; view?: string; mini?: boolean; yr: string; kindLabel?: string | undefined;
  /** Afbeelding meteen laden; standaard bij mini, anders lazy. */
  eager?: boolean;
  /** Beschrijving van de afbeelding voor zoekmachines en schermlezers (ADR 0055); standaard de naam van de plaat. */
  alt?: string | undefined;
  pick?: { selected: boolean; onToggle: () => void };
}) {
  return <CardView card={cardOf(plate, taxonomy, view, { kindLabel, alt })} base={base} eager={eager} yr={yr} {...(pick ? { pick } : {})} />;
}

/** De kaart zelf, uit al uitgerekende gegevens; ook voor PlateGrid (ADR 0099). */
export function CardView({ card, base, eager = false, yr, pick }: {
  card: CardData; base: string; eager?: boolean; yr: string;
  pick?: { selected: boolean; onToggle: () => void };
}) {
  const body = (
    <>
      {pick && <span className="tick" aria-hidden="true">{pick.selected ? "✓" : ""}</span>}
      {card.kindLabel && <span className="kind-badge">{card.kindLabel}</span>}
      <div className="paper"><PlateImage src={card.svg} alt={card.alt ?? card.name} eager={eager} /></div>
      <b>{card.name}</b>
      <em><i />{card.label}<span className="yr">{card.age.replace("-", "–")} {yr}</span></em>
    </>
  );
  const style = { "--c": card.color } as CSSProperties;
  if (pick) return <button type="button" className="card" style={style} aria-pressed={pick.selected} onClick={pick.onToggle}>{body}</button>;
  return <Link href={link(base, `/platen/${card.slug}`)} className="card" style={style}>{body}</Link>;
}
