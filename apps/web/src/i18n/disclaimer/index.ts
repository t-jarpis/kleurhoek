import type { ComponentType } from "react";
import { Disclaimer as nl } from "./nl";
import type { DisclaimerProps } from "./types";

const all: Record<string, ComponentType<DisclaimerProps>> = { nl };
/** De disclaimer in de taal van de markt; zonder vertaling de Nederlandse. */
export const disclaimer = (language: string): ComponentType<DisclaimerProps> => all[language] ?? nl;
