import Link from "next/link";
import type { CSSProperties } from "react";
import type { PlateItem, Taxonomy } from "@/lib/types";
import { link } from "@/lib/sites";
import { labelFor } from "./labels";

/**
 * Een plaat in het raster. Normaal een link naar de kleurstudio; tijdens het kiezen voor een boekje
 * een knop die de plaat aan- of uitzet.
 */
export function PlateCard({ plate, base, taxonomy, view = "alle", mini = false, yr, pick, kindLabel, alt }: {
  plate: PlateItem; base: string; taxonomy: Taxonomy; view?: string; mini?: boolean; yr: string; kindLabel?: string | undefined;
  /** Beschrijving van de afbeelding voor zoekmachines en schermlezers (ADR 0055); standaard de naam van de plaat. */
  alt?: string | undefined;
  pick?: { selected: boolean; onToggle: () => void };
}) {
  const label = labelFor(plate, taxonomy, view);
  const body = (
    <>
      {pick && <span className="tick" aria-hidden="true">{pick.selected ? "✓" : ""}</span>}
      {kindLabel && <span className="kind-badge">{kindLabel}</span>}
      <div className="paper"><img src={plate.svg} alt={alt ?? plate.name} loading={mini ? "eager" : "lazy"} width={200} height={200} /></div>
      <b>{plate.name}</b>
      <em><i />{label.text}<span className="yr">{plate.age.replace("-", "–")} {yr}</span></em>
    </>
  );
  const style = { "--c": label.color } as CSSProperties;
  if (pick) return <button type="button" className="card" style={style} aria-pressed={pick.selected} onClick={pick.onToggle}>{body}</button>;
  return <Link href={link(base, `/platen/${plate.slug}`)} className="card" style={style}>{body}</Link>;
}
