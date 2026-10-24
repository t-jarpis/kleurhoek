/**
 * Rapporten van partners inlezen (ADR 0033): een CSV uit het partneraccount (bol, Amazon, een netwerk) wordt
 * rijen met datum, sub-ID, product, aantal, omzet en commissie. Pure functies, zonder database.
 */

export const SALES_FIELDS = ["date", "subId", "product", "items", "revenue", "commission", "currency"] as const;
export type SalesField = (typeof SALES_FIELDS)[number];
/** Per gegeven de kolomkop in het bestand, of null als het er niet in staat. */
export type SalesMapping = Record<SalesField, string | null>;

/** Kolomkoppen die we herkennen (kleine letters, zonder valutateken), in volgorde van voorkeur. */
const SYNONYMS: Record<SalesField, string[]> = {
  date: ["date shipped", "verzenddatum", "versanddatum", "datum verzonden", "order date", "besteldatum", "bestelldatum", "datum", "date", "day", "dag"],
  subId: ["tracking id", "tracking-id", "trackingid", "sub id", "subid", "sub-id", "subid1", "name", "naam", "kenmerk", "reference", "referentie"],
  product: ["asin", "ean", "product id", "productid", "productcode", "product code", "artikelnummer", "sku"],
  items: ["items shipped", "aantal", "quantity", "qty", "items", "stuks", "anzahl", "verkochte artikelen"],
  revenue: ["revenue", "omzet", "umsatz", "sales", "bedrag", "price", "prijs", "order value", "orderwaarde"],
  commission: ["ad fees", "advertising fees", "commissie", "commission", "vergoeding", "provision", "werbekostenerstattung", "earnings", "verdiensten"],
  currency: ["currency", "valuta", "währung"],
};

const norm = (h: string) => h.toLowerCase().replace(/\(.*?\)|[€$£]|\s+/g, " ").replace(/\s+/g, " ").trim();

/** CSV inlezen: komma, puntkomma of tab; aanhalingstekens; een BOM; regels vóór de kopregel (titels) slaan we over. */
export function parseCsv(text: string): { headers: string[]; rows: string[][] } {
  const clean = text.replace(/^﻿/, "");
  const firstLines = clean.split(/\r?\n/).slice(0, 10).join("\n");
  const delim = [",", ";", "\t"].map((d) => [d, (firstLines.match(new RegExp(d === "\t" ? "\t" : `\\${d}`, "g")) ?? []).length] as const).sort((a, b) => b[1] - a[1])[0]![0];
  const rows: string[][] = [];
  let row: string[] = [], cell = "", quoted = false;
  for (let i = 0; i < clean.length; i++) {
    const ch = clean[i]!;
    if (quoted) {
      if (ch === '"' && clean[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') quoted = false; else cell += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === delim) { row.push(cell.trim()); cell = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && clean[i + 1] === "\n") i++;
      row.push(cell.trim()); cell = "";
      if (row.some((c) => c !== "")) rows.push(row);
      row = [];
    } else cell += ch;
  }
  row.push(cell.trim());
  if (row.some((c) => c !== "")) rows.push(row);
  // Kopregel: de eerste regel waarin minstens twee bekende koppen staan.
  const known = Object.values(SYNONYMS).flat();
  const at = rows.findIndex((r) => r.filter((c) => known.includes(norm(c))).length >= 2);
  const head = at >= 0 ? at : 0;
  return { headers: rows[head] ?? [], rows: rows.slice(head + 1).filter((r) => r.length > 1) };
}

/** Kolommen herkennen aan hun kop. */
export function detectMapping(headers: string[]): SalesMapping {
  const out = {} as SalesMapping;
  const used = new Set<string>();
  for (const field of SALES_FIELDS) {
    let hit: string | null = null;
    for (const syn of SYNONYMS[field]) {
      hit = headers.find((h) => !used.has(h) && norm(h) === syn) ?? null;
      if (hit) break;
    }
    if (hit) used.add(hit);
    out[field] = hit;
  }
  return out;
}

/** Bedrag in centen: "1.234,56", "1,234.56", "€ 8,99", "-0,50". null als het geen getal is. */
export function parseAmount(raw: string | undefined): number | null {
  if (raw == null) return null;
  let s = raw.replace(/[^\d,.-]/g, "");
  if (!/\d/.test(s)) return null;
  const lastComma = s.lastIndexOf(","), lastDot = s.lastIndexOf(".");
  if (lastComma > lastDot) s = s.replace(/\./g, "").replace(",", ".");
  else s = s.replace(/,/g, "");
  const n = Number(s);
  return Number.isFinite(n) ? Math.round(n * 100) : null;
}

/** Valuta uit een kop als "Revenue(€)" of "Omzet (EUR)". */
export function currencyFromHeader(h: string | null): string | null {
  if (!h) return null;
  if (/€|eur/i.test(h)) return "EUR";
  if (/£|gbp/i.test(h)) return "GBP";
  if (/zł|pln/i.test(h)) return "PLN";
  if (/sek|kr\b/i.test(h)) return "SEK";
  if (/\$|usd/i.test(h)) return "USD";
  return null;
}

const MONTHS: Record<string, number> = { jan: 1, feb: 2, mar: 3, mrt: 3, apr: 4, may: 5, mei: 5, mai: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, okt: 10, nov: 11, dec: 12, dez: 12 };

/** Datum als YYYY-MM-DD: ISO, dag-maand-jaar (Europees) of "October 24, 2026". null als het geen datum is. */
export function parseDay(raw: string | undefined): string | null {
  if (!raw) return null;
  const s = raw.trim();
  const pad = (n: number) => String(n).padStart(2, "0");
  const ok = (y: number, m: number, d: number) => (m >= 1 && m <= 12 && d >= 1 && d <= 31 && y >= 2000 && y < 2100 ? `${y}-${pad(m)}-${pad(d)}` : null);
  let m = /^(\d{4})-(\d{1,2})-(\d{1,2})/.exec(s);
  if (m) return ok(+m[1]!, +m[2]!, +m[3]!);
  m = /^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})/.exec(s);
  if (m) return ok(+m[3]!, +m[2]!, +m[1]!);
  m = /^([a-z]{3})[a-z]*\.? (\d{1,2}),? (\d{4})/i.exec(s);
  if (m && MONTHS[m[1]!.toLowerCase()]) return ok(+m[3]!, MONTHS[m[1]!.toLowerCase()]!, +m[2]!);
  m = /^(\d{1,2})\.? ([a-z]{3})[a-z]*\.? (\d{4})/i.exec(s);
  if (m && MONTHS[m[2]!.toLowerCase()]) return ok(+m[3]!, MONTHS[m[2]!.toLowerCase()]!, +m[1]!);
  return null;
}

export interface SalesRow { day: string; subId: string; product: string; items: number; revenueCents: number; commissionCents: number; currency: string }

/** Rijen omzetten met de gekozen kolommen. Rijen zonder datum of commissie tellen als fout (bijvoorbeeld een totaalregel). */
export function toRows(parsed: { headers: string[]; rows: string[][] }, mapping: SalesMapping, fallbackCurrency = "EUR") {
  const col = (f: SalesField) => (mapping[f] ? parsed.headers.indexOf(mapping[f]!) : -1);
  const idx = Object.fromEntries(SALES_FIELDS.map((f) => [f, col(f)])) as Record<SalesField, number>;
  const headerCurrency = currencyFromHeader(mapping.commission) ?? currencyFromHeader(mapping.revenue) ?? fallbackCurrency;
  const rows: SalesRow[] = [];
  let skipped = 0;
  for (const r of parsed.rows) {
    const day = parseDay(r[idx.date]);
    const commission = parseAmount(r[idx.commission]);
    if (!day || commission === null) { skipped++; continue; }
    const items = idx.items >= 0 ? Number((r[idx.items] ?? "").replace(/[^\d-]/g, "")) || 0 : 1;
    rows.push({
      day, commissionCents: commission, items,
      subId: idx.subId >= 0 ? (r[idx.subId] ?? "").slice(0, 100) : "",
      product: idx.product >= 0 ? (r[idx.product] ?? "").trim().toUpperCase().slice(0, 40) : "",
      revenueCents: idx.revenue >= 0 ? parseAmount(r[idx.revenue]) ?? 0 : 0,
      currency: idx.currency >= 0 && /^[A-Z]{3}$/i.test(r[idx.currency] ?? "") ? r[idx.currency]!.toUpperCase() : headerCurrency,
    });
  }
  return { rows, skipped };
}
