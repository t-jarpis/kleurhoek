import type { Messages } from "./nl-base";
import { MARKET_VARIANTS, resolve } from "./variants";

/**
 * Teksten voor de browser (ADR 0081): alleen de taal van de pagina, als eigen bestand (chunk) per taal, met de
 * variant van de markt erop. Eén belofte per markt, zodat use() in I18nProvider steeds dezelfde krijgt.
 */
const LOADERS: Record<string, () => Promise<Messages>> = {
  nl: () => import("./nl-base").then((m) => m.nl), de: () => import("./de").then((m) => m.de), en: () => import("./en").then((m) => m.en),
  es: () => import("./es").then((m) => m.es), fr: () => import("./fr").then((m) => m.fr), it: () => import("./it").then((m) => m.it),
  pl: () => import("./pl").then((m) => m.pl), pt: () => import("./pt").then((m) => m.pt), sv: () => import("./sv").then((m) => m.sv),
  da: () => import("./da").then((m) => m.da), nb: () => import("./nb").then((m) => m.nb), fi: () => import("./fi").then((m) => m.fi),
  cs: () => import("./cs").then((m) => m.cs), sk: () => import("./sk").then((m) => m.sk), hu: () => import("./hu").then((m) => m.hu),
  ro: () => import("./ro").then((m) => m.ro), el: () => import("./el").then((m) => m.el), bg: () => import("./bg").then((m) => m.bg),
  hr: () => import("./hr").then((m) => m.hr), sl: () => import("./sl").then((m) => m.sl), et: () => import("./et").then((m) => m.et),
  lv: () => import("./lv").then((m) => m.lv), lt: () => import("./lt").then((m) => m.lt), uk: () => import("./uk").then((m) => m.uk),
  tr: () => import("./tr").then((m) => m.tr), sr: () => import("./sr").then((m) => m.sr), mk: () => import("./mk").then((m) => m.mk),
  sq: () => import("./sq").then((m) => m.sq), is: () => import("./is").then((m) => m.is),
};

const cache = new Map<string, Promise<Messages>>();

export function loadMessages(marketOrLanguage: string): Promise<Messages> {
  const key = marketOrLanguage.toLowerCase();
  let p = cache.get(key);
  if (!p) {
    const { language, variant } = resolve(key);
    p = LOADERS[language]!().then((m) => (variant ? MARKET_VARIANTS[variant]!(m) : m));
    cache.set(key, p);
  }
  return p;
}

export const LOADED_LANGUAGES = Object.keys(LOADERS);
