"use client";
import { createContext, use, useContext } from "react";
import { loadMessages } from "@/i18n/load";
import type { Messages } from "@/i18n/nl-base";

/**
 * Teksten in de browser (ADR 0081): de layout zet de markt, de provider laadt alleen die taal (één bestand) en
 * client components lezen hem met useT(). Server components blijven messages() uit i18n/nl gebruiken.
 */
const I18nContext = createContext<Messages | null>(null);

export function I18nProvider({ market, children }: { market: string; children: React.ReactNode }) {
  const t = use(loadMessages(market));
  return <I18nContext.Provider value={t}>{children}</I18nContext.Provider>;
}

export function useT(): Messages {
  const t = useContext(I18nContext);
  if (!t) throw new Error("useT() buiten I18nProvider");
  return t;
}
