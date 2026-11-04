import { de } from "./de";
import { en } from "./en";
import { es } from "./es";
import { fr } from "./fr";
import { it } from "./it";
import { pl } from "./pl";
import { pt } from "./pt";
import { sv } from "./sv";
import { da } from "./da";
import { nb } from "./nb";
import { fi } from "./fi";
import { cs } from "./cs";
import { sk } from "./sk";
import { hu } from "./hu";
import { ro } from "./ro";
import { el } from "./el";
import { bg } from "./bg";
import { hr } from "./hr";
import { sl } from "./sl";
import { et } from "./et";
import { lv } from "./lv";
import { lt } from "./lt";
import { uk } from "./uk";
import { tr } from "./tr";
import { sr } from "./sr";
import { mk } from "./mk";
import { sq } from "./sq";
import { is } from "./is";
import { nl, type Messages } from "./nl-base";
import { LANGUAGES, MARKET_VARIANTS, resolve } from "./variants";

export { nl, type Messages };
export { swissSpelling, usSpelling } from "./variants";

/**
 * Teksten voor de server: alle talen vooraf geladen (ADR 0029). Client components gebruiken useT() uit
 * components/I18n.tsx, dat alleen de eigen taal laadt (ADR 0081). Elke taal een eigen bestand met dezelfde sleutels.
 */
const base: Record<string, Messages> = { nl, de, en, es, fr, it, pl, pt, sv, da, nb, fi, cs, sk, hu, ro, el, bg, hr, sl, et, lv, lt, uk, tr, sr, mk, sq, is };
const cache = new Map<string, Messages>();

/** Teksten voor een markt ("en-us") of een taal ("en"). Een markt zonder eigen variant krijgt zijn taal. */
export const messages = (marketOrLanguage: string): Messages => {
  const { language, variant } = resolve(marketOrLanguage);
  if (!variant) return base[language]!;
  let m = cache.get(variant);
  if (!m) { m = MARKET_VARIANTS[variant]!(base[language]!); cache.set(variant, m); }
  return m;
};

// Elke taal in LANGUAGES moet hier ook staan.
void LANGUAGES;
