import type { Messages } from "@/i18n/nl";
import type { PlateDetail } from "@/lib/types";
import { SeenTracker } from "./SeenTracker";

/**
 * Onder de plaat, voor de volwassene die print: hoe je het maakt, op welk papier, en wat je nodig
 * hebt. Producten staan alleen hier, duidelijk gemarkeerd als partnerlink, nooit in de kleurstudio
 * en nooit gericht op kinderen (ADR 0011).
 */
export function ForParents({ plate, market, t }: { plate: PlateDetail; market: string; t: Messages }) {
  const craft = plate.kind !== "kleurplaat";
  const withProducts = plate.materials.filter((m) => m.product);
  const facts = [
    plate.minutes ? t.aboutMinutes(plate.minutes) : null,
    plate.adultHelp ? t.adultHelp : null,
    plate.paperGsm ? t.paper(plate.paperGsm) : null,
  ].filter((f): f is string => !!f);
  if (!craft && !plate.materials.length) return null;
  return (
    <section className="parents no-print" aria-labelledby="voor-ouders">
      <div className="parents-head">
        <p className="eyebrow">{t.forParents}</p>
        <h2 id="voor-ouders">{craft ? t.howToMake : t.whatYouNeed}</h2>
        {facts.length > 0 && <p className="facts-line">{facts.join(" · ")}</p>}
      </div>
      {craft && plate.steps.length > 0 && (
        <ol className="steps">{plate.steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
      )}
      {plate.printNote && <p className="hint">{plate.printNote}</p>}
      {plate.materials.length > 0 && (
        <div className="needs">
          {craft && <h3>{t.whatYouNeed}</h3>}
          <ul>
            {plate.materials.map((m) => (
              <li key={m.slug}>
                <span><span className="nm"><b>{m.name}</b>{m.optional && <em> · {t.optional}</em>}</span>{m.hint && <small>{m.hint}</small>}</span>
                {m.product && (
                  <a className="offer" href={`/ga/${m.product.slug}?plaat=${plate.slug}&m=${market}`} rel="sponsored nofollow noopener" target="_blank">
                    <span>{m.product.name}{m.product.priceHint ? ` · ${m.product.priceHint}` : ""}</span><small>{t.atPartner(m.product.partner)}</small>
                  </a>
                )}
              </li>
            ))}
          </ul>
          {withProducts.length > 0 && <p className="disclosure">{t.partnerDisclosure}</p>}
          <SeenTracker event={{ type: "materials_view", market, plate: plate.slug }} />
        </div>
      )}
    </section>
  );
}
