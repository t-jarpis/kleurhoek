import type { Fills } from "./studio";

/**
 * Delen vanuit de kleurstudio (ADR 0074). Een ingekleurde plaat reist mee in de link zelf (`?k=`), zodat er
 * niets op de server bewaard wordt. Alleen vlakkleuren gaan mee: geen penseelstreken en nooit de eigen tekst
 * (vaak een naam). `?d=1` zegt dat iemand via een gedeelde link binnenkwam; we tellen dat zonder cookies.
 *
 * Vorm van `k`: kleuren zonder # gescheiden door punten, dan `~`, dan per vlak één teken: het nummer van de
 * kleur (0-9, a-z) of `-` voor leeg. Voorbeeld: `e2483d.f2c618~01-1`.
 */
export const SHARE_PARAM = "k";
export const SHARED_FLAG = "d";
const MAX_COLORS = 36;
const DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz";
const HEX = /^#?([0-9a-f]{6})$/i;

/** Effen kleur van een vulling; verloop of patroon worden hun eerste kleur (zelfde als de pipet). */
export type ColorOf = (value: string | undefined) => string | null;

export function encodeFills(fills: Fills, regionCount: number, colorOf: ColorOf): string | null {
  const colors: string[] = [];
  const cells: string[] = [];
  for (let i = 0; i < regionCount; i++) {
    const hex = HEX.exec(colorOf(fills[i]) ?? "")?.[1]?.toLowerCase();
    if (!hex) { cells.push("-"); continue; }
    let at = colors.indexOf(hex);
    if (at < 0 && colors.length < MAX_COLORS) { colors.push(hex); at = colors.length - 1; }
    cells.push(at < 0 ? "-" : DIGITS[at]!);
  }
  const body = cells.join("").replace(/-+$/, "");
  return colors.length ? `${colors.join(".")}~${body}` : null;
}

/** Terug naar vlakkleuren. Alles wat niet klopt (te veel vlakken, onbekende kleur) geeft null: dan negeren we de link. */
export function decodeFills(k: string | null | undefined, regionCount: number): Fills | null {
  if (!k || k.length > 2000) return null;
  const m = /^([0-9a-f]{6}(?:\.[0-9a-f]{6}){0,35})~([0-9a-z-]*)$/.exec(k.toLowerCase());
  if (!m) return null;
  const colors = m[1]!.split(".");
  const cells = m[2]!;
  if (cells.length > regionCount) return null;
  const fills: Fills = {};
  for (let i = 0; i < cells.length; i++) {
    const c = cells[i]!;
    if (c === "-") continue;
    const at = DIGITS.indexOf(c);
    if (at < 0 || at >= colors.length) return null;
    fills[i] = `#${colors[at]}`;
  }
  return fills;
}

/** Link naar deze plaat om te delen: leeg, of met de kleuren erin. */
export function shareUrl(pageUrl: string, k?: string | null): string {
  const u = new URL(pageUrl);
  u.search = "";
  u.hash = "";
  if (k) u.searchParams.set(SHARE_PARAM, k);
  u.searchParams.set(SHARED_FLAG, "1");
  return u.toString();
}

/** WhatsApp-link met tekst en link (werkt op telefoon en computer). */
export const whatsappUrl = (text: string, url: string) => `https://wa.me/?${new URLSearchParams({ text: `${text} ${url}` })}`;
