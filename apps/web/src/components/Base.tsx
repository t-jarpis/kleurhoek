"use client";
import { createContext, useContext } from "react";
import { link, type SiteEntry } from "@/lib/sites";

/**
 * Het voorvoegsel van links in deze markt ("", "/fr" of "/de-de") en de markten voor de taalkeuze, gezet in de
 * layout (ADR 0040).
 */
const BaseContext = createContext<{ base: string; market: string; sites: SiteEntry[] }>({ base: "", market: "", sites: [] });

export function BaseProvider({ base, market, sites, children }: { base: string; market: string; sites: SiteEntry[]; children: React.ReactNode }) {
  return <BaseContext.Provider value={{ base, market, sites }}>{children}</BaseContext.Provider>;
}

export const useBase = () => useContext(BaseContext).base;
export const useSites = () => useContext(BaseContext);
/** `href("/platen/kat")` → link in de huidige markt. */
export const useHref = () => { const base = useBase(); return (path = "") => link(base, path); };
