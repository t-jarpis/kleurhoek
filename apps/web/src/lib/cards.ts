import type { PlateItem, Taxonomy } from "./types";
import { labelFor } from "@/components/labels";

/** Wat een kaart in het raster toont; alles al op de server uitgerekend (label, kleur, alt). */
export interface CardData {
  slug: string; name: string; svg: string; label: string; color: string; age: string;
  kindLabel?: string | undefined;
  /** Beschrijving van de afbeelding; zonder: de naam. */
  alt?: string | undefined;
}

/**
 * Kaart als korte rij voor een client component (ADR 0099): [slug, naam, svg, label, kleur, leeftijd, soort, alt].
 * Het svg-adres zonder het vaste begin `/v1/assets/plates/<slug>/`; soort en alt leeg als ze niets toevoegen.
 * Zo is een kaart in de pagina ongeveer 110 tekens in plaats van ruim 500 als React-boom.
 */
export type PackedCard = [string, string, string, string, string, string, string?, string?];

const svgPrefix = (slug: string) => `/v1/assets/plates/${slug}/`;

export function packCard(c: CardData): PackedCard {
  const prefix = svgPrefix(c.slug);
  const svg = c.svg.startsWith(prefix) ? c.svg.slice(prefix.length) : c.svg;
  const alt = c.alt && c.alt !== c.name ? c.alt : "";
  const row: PackedCard = [c.slug, c.name, svg, c.label, c.color, c.age];
  if (c.kindLabel || alt) row.push(c.kindLabel ?? "");
  if (alt) row.push(alt);
  return row;
}

export function unpackCard([slug, name, svg, label, color, age, kindLabel, alt]: PackedCard): CardData {
  return { slug, name, svg: svg.startsWith("/") ? svg : svgPrefix(slug) + svg, label, color, age, kindLabel: kindLabel || undefined, alt: alt || undefined };
}

/** Van een plaat uit de API naar een kaart, met het label zoals PlateCard dat kiest. */
export function cardOf(p: PlateItem, taxonomy: Taxonomy, view: string, extra: { kindLabel?: string | undefined; alt?: string | undefined } = {}): CardData {
  const label = labelFor(p, taxonomy, view);
  return { slug: p.slug, name: p.name, svg: p.svg, label: label.text, color: label.color, age: p.age, kindLabel: extra.kindLabel, alt: extra.alt };
}
