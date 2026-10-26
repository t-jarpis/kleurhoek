import type { ComponentType } from "react";
import { Disclaimer as de } from "./de";
import { Disclaimer as en } from "./en";
import { Disclaimer as es } from "./es";
import { Disclaimer as fr } from "./fr";
import { Disclaimer as it } from "./it";
import { Disclaimer as nl } from "./nl";
import { Disclaimer as pl } from "./pl";
import { Disclaimer as pt } from "./pt";
import type { DisclaimerProps } from "./types";

const all: Record<string, ComponentType<DisclaimerProps>> = { nl, de, en, es, fr, it, pl, pt };
/** De disclaimer in de taal van de markt; zonder vertaling de Nederlandse. */
export const disclaimer = (language: string): ComponentType<DisclaimerProps> => all[language] ?? nl;
