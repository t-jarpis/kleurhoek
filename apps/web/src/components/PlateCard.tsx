import Link from "next/link";
import type { CSSProperties } from "react";
import type { PlateItem, Taxonomy } from "@/lib/types";
import { labelFor } from "./labels";

export function PlateCard({ plate, market, taxonomy, view = "alle", mini = false, yr }: { plate: PlateItem; market: string; taxonomy: Taxonomy; view?: string; mini?: boolean; yr: string }) {
  const label = labelFor(plate, taxonomy, view);
  const age = taxonomy.ages.find((a) => a.slug === plate.age);
  return (
    <Link href={`/${market}/platen/${plate.slug}`} className="card" style={{ "--c": label.color } as CSSProperties}>
      <div className="paper"><img src={plate.svg} alt="" loading={mini ? "eager" : "lazy"} width={200} height={200} /></div>
      <b>{plate.name}</b>
      <em><i />{label.text}<span className="yr">{age ? age.name.replace(/ jaar$/, "") : plate.age} {yr}</span></em>
    </Link>
  );
}
