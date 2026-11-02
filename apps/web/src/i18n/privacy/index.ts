import { en } from "./en";
import { nl } from "./nl";
import type { PrivacyText } from "./types";

/** Privacybeleid (ADR 0069): Nederlands en Engels; andere talen krijgen de Engelse tekst. */
export const privacy = (language: string): { text: PrivacyText; lang: string } => (language === "nl" ? { text: nl, lang: "nl" } : { text: en, lang: "en" });
