"use client";
import { unpackCard, type PackedCard } from "@/lib/cards";
import { CardView } from "./PlateCard";

/**
 * Een lange rij kaarten (onderwerppagina's, ADR 0099). Dezelfde HTML als PlateCard op de server, maar de pagina
 * stuurt per kaart een korte rij mee in plaats van de hele React-boom: bij 400+ kaarten scheelt dat honderden kB.
 */
export function PlateGrid({ cards, base, yr }: { cards: PackedCard[]; base: string; yr: string }) {
  return cards.map((row) => { const card = unpackCard(row); return <CardView key={card.slug} card={card} base={base} yr={yr} />; });
}
