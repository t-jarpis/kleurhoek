import { en } from "./en";
import { nl } from "./nl";
import { text as de } from "./de";
import { text as fr } from "./fr";
import { text as es } from "./es";
import { text as it } from "./it";
import { text as pt } from "./pt";
import { text as sv } from "./sv";
import { text as da } from "./da";
import { text as nb } from "./nb";
import { text as fi } from "./fi";
import { text as pl } from "./pl";
import { text as cs } from "./cs";
import { text as sk } from "./sk";
import { text as hu } from "./hu";
import { text as ro } from "./ro";
import { text as el } from "./el";
import { text as bg } from "./bg";
import { text as hr } from "./hr";
import { text as sl } from "./sl";
import { text as et } from "./et";
import { text as lv } from "./lv";
import { text as lt } from "./lt";
import { text as uk } from "./uk";
import { text as tr } from "./tr";
import { text as sr } from "./sr";
import { text as mk } from "./mk";
import { text as sq } from "./sq";
import { text as is_ } from "./is";
import type { PrivacyText } from "./types";

const TEXTS: Record<string, PrivacyText> = { nl, en, de: de, fr: fr, es: es, it: it, pt: pt, sv: sv, da: da, nb: nb, fi: fi, pl: pl, cs: cs, sk: sk, hu: hu, ro: ro, el: el, bg: bg, hr: hr, sl: sl, et: et, lv: lv, lt: lt, uk: uk, tr: tr, sr: sr, mk: mk, sq: sq, is: is_ };

/** Privacybeleid (ADR 0069): in elke taal van de site; een onbekende taal krijgt Engels. */
export const privacy = (language: string): { text: PrivacyText; lang: string } =>
  TEXTS[language] ? { text: TEXTS[language]!, lang: language } : { text: en, lang: "en" };
