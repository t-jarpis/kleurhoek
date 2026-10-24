"use strict";
// Tekstlaag van platen (ADR 0029). De teksten in een plaat staan in de brontaal (nl) in de SVG. Voor een
// andere taal vervangen we elke <text> op het moment van serveren door de vertaling uit de woordenlijst
// (bronzin → vertaling). Een langere vertaling krijgt een kleinere letter, zodat hij in dezelfde ruimte past.
// Gedeeld door de API (serveren, zichtbaarheid) en de scripts (controle per taal).

const SOURCE_LANGUAGE = "nl";
const TEXT = /<text\b([^>]*)>([^<]*)<\/text>/g;

const decode = (s) => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&");
const encode = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const norm = (s) => decode(s).replace(/\s+/g, " ").trim();

/** Tekst zonder letters (getallen, sommen, tekens) of één losse letter (A, B als label) hoeft niet vertaald. */
function isNeutral(text) {
  const t = text.replace(/\s+/g, "");
  if (!/\p{L}/u.test(t)) return true;
  return /^\p{L}[.)]?$/u.test(t);
}

/** Alle te vertalen bronteksten in een of meer SVG's, uniek, in volgorde van voorkomen. */
function plateTexts(...svgs) {
  const seen = new Set();
  for (const svg of svgs) for (const m of svg.matchAll(TEXT)) {
    const t = norm(m[2]);
    if (t && !isNeutral(t)) seen.add(t);
  }
  return [...seen];
}

/** Ruwe schatting van de breedte: smalle en brede letters tellen anders mee. Alleen voor verhoudingen. */
function width(s) {
  let w = 0;
  for (const ch of s) {
    if (/[iljtfrIJ.,:;'!|() ]/.test(ch)) w += 0.55;
    else if (/[mwMW]/.test(ch)) w += 1.45;
    else if (/\p{Lu}/u.test(ch)) w += 1.2;
    else w += 1;
  }
  return w;
}

const DEFAULT_SIZE = { tip: 6 };

/**
 * Vervang de teksten door vertalingen. `lookup(bron)` geeft de vertaling of undefined.
 * Geeft de nieuwe SVG, de ontbrekende bronteksten en per tekst de schaal (voor de controle).
 */
function localizeSvg(svg, lookup) {
  const missing = new Set();
  const scaled = [];
  const out = svg.replace(TEXT, (whole, attrs, content) => {
    const src = norm(content);
    if (!src || isNeutral(src)) return whole;
    const tr = lookup(src);
    if (tr == null || tr === "") { missing.add(src); return whole; }
    let a = attrs;
    const ratio = width(tr) / Math.max(width(src), 0.5);
    if (ratio > 1.05) {
      const sizeAttr = /\sfont-size="([\d.]+)"/.exec(a);
      const styleSize = /font-size:\s*([\d.]+)/.exec(a);
      const cls = /\sclass="([^"]*)"/.exec(a)?.[1] ?? "";
      // De CSS van .tip zet de lettergrootte vast en wint van het attribuut; een inline stijl wint van allebei.
      const base = Number(styleSize?.[1] ?? DEFAULT_SIZE[cls] ?? sizeAttr?.[1] ?? 16);
      // Niet kleiner dan 4,5 (leesbaar geprint) en niet kleiner dan 70% van het origineel: een wat langere tekst
      // mag iets buiten zijn ruimte lopen; check-lang.mjs meldt als hij dan iets anders raakt of van het vel valt.
      const floor = Math.max(Math.min(base, 4.5), base * 0.7);
      const size = Math.round(Math.max(base / ratio, floor) * 100) / 100;
      scaled.push({ source: src, text: tr, from: base, to: size });
      if (sizeAttr) a = a.replace(/\sfont-size="[\d.]+"/, ` font-size="${size}"`);
      if (styleSize) a = a.replace(/font-size:\s*[\d.]+(px)?/, `font-size:${size}px`);
      else a = /\sstyle="/.test(a) ? a.replace(/\sstyle="/, ` style="font-size:${size}px;`) : `${a} style="font-size:${size}px"`;
    }
    return `<text${a}>${encode(tr)}</text>`;
  });
  return { svg: out, missing: [...missing], scaled };
}

module.exports = { SOURCE_LANGUAGE, isNeutral, plateTexts, localizeSvg, width };
