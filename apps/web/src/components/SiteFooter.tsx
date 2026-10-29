import Link from "next/link";
import { link } from "@/lib/sites";
import { MarketLinks } from "./MarketSwitch";
import type { Messages } from "@/i18n/nl";

/** Onderaan elke pagina: disclaimer, contact en de Bronnengids (ADR 0024, 0025, 0028). */
/** `own` = link naar "Eigen omgeving" tonen; alleen op Kleurhoek zelf, niet op de site van een organisatie. */
export function SiteFooter({ base, t, own = false }: { base: string; t: Messages; own?: boolean }) {
  return (
    <footer className="kh-footer no-print">
      <nav aria-label="Over Kleurhoek">
        <Link href={link(base, "/themas")}>{t.themes}</Link>
        <Link href={link(base, "/aftelkalender")}>{t.advent.nav}</Link>
        <Link href={link(base, "/lespakketten")}>{t.packs.nav}</Link>
        <Link href={link(base, "/samen")}>{t.together.nav}</Link>
        {own && <Link href={link(base, "/eigen-omgeving")}>{t.ownSpace}</Link>}
        {own && <Link href={link(base, "/mail")}>{t.mlAccount}</Link>}
        <Link href={link(base, "/contact")}>{t.contact}</Link>
        <Link href={link(base, "/disclaimer")}>{t.disclaimer}</Link>
        {/* Op de site van een organisatie: ingang voor wie het aanbod beheert (ADR 0036). */}
        {!own && <Link href={link(base, "/beheer")} rel="nofollow">{t.mgFooter}</Link>}
      </nav>
      <MarketLinks label={t.marketsLabel} />
      <p>{t.note}</p>
    </footer>
  );
}
