import Link from "next/link";
import type { CSSProperties } from "react";
import type { Messages } from "@/i18n/nl";
import { link } from "@/lib/sites";
import { DIMENSIONS, type Dimension, type Topic } from "@/lib/topics";

/**
 * TopicLinks uit het design system (ADR 0055): links naar alle onderwerppagina's van een markt, per groep. Echte
 * pagina's, geen ?-filters, zodat elke plaat met een paar klikken bereikbaar is voor bezoekers en zoekmachines.
 */
export function TopicLinks({ groups, base, t, current }: { groups: Record<Dimension, Topic[]>; base: string; t: Messages; current?: string }) {
  return (
    <section className="ui-topiclinks no-print">
      {DIMENSIONS.filter((d) => groups[d].length > 1).map((d) => (
        <div key={d}>
          <h2>{t.topicGroups[d]}</h2>
          <ul>
            {groups[d].map((x) => (
              <li key={x.slug}>
                <Link className="ui-chip" href={link(base, x.path)} aria-current={current === x.path ? "page" : undefined}
                  style={x.color ? ({ "--chip-color": x.color } as CSSProperties) : undefined}>
                  <span className="ui-chip-dot" />{x.name}<span className="ui-chip-count">{x.count}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
