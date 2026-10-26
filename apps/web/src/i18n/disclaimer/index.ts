import type { ComponentType } from "react";
import { Disclaimer as de } from "./de";
import { Disclaimer as en } from "./en";
import { Disclaimer as es } from "./es";
import { Disclaimer as fr } from "./fr";
import { Disclaimer as it } from "./it";
import { Disclaimer as nl } from "./nl";
import { Disclaimer as pl } from "./pl";
import { Disclaimer as pt } from "./pt";
import { Disclaimer as sv } from "./sv";
import { Disclaimer as da } from "./da";
import { Disclaimer as nb } from "./nb";
import { Disclaimer as fi } from "./fi";
import { Disclaimer as cs } from "./cs";
import { Disclaimer as sk } from "./sk";
import { Disclaimer as hu } from "./hu";
import { Disclaimer as ro } from "./ro";
import { Disclaimer as el } from "./el";
import type { DisclaimerProps } from "./types";

const all: Record<string, ComponentType<DisclaimerProps>> = { nl, de, en, es, fr, it, pl, pt, sv, da, nb, fi, cs, sk, hu, ro, el };
/** De disclaimer in de taal van de markt; zonder vertaling de Nederlandse. */
export const disclaimer = (language: string): ComponentType<DisclaimerProps> => all[language] ?? nl;
