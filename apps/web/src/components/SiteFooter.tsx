import Link from "next/link";
import type { Messages } from "@/i18n/nl";

/** Onderaan elke pagina: disclaimer, contact en de Bronnengids (ADR 0024, 0025, 0028). */
/** `own` = link naar "Eigen omgeving" tonen; alleen op Kleurhoek zelf, niet op de site van een organisatie. */
export function SiteFooter({ market, t, own = false }: { market: string; t: Messages; own?: boolean }) {
  return (
    <footer className="kh-footer no-print">
      <nav aria-label="Over Kleurhoek">
        <Link href={`/${market}/themas`}>{t.themes}</Link>
        {own && <Link href={`/${market}/eigen-omgeving`}>{t.ownSpace}</Link>}
        <Link href={`/${market}/contact`}>{t.contact}</Link>
        <Link href={`/${market}/disclaimer`}>{t.disclaimer}</Link>
        {/* Op de site van een organisatie: ingang voor wie het aanbod beheert (ADR 0036). */}
        {!own && <Link href={`/${market}/beheer`} rel="nofollow">{t.mgFooter}</Link>}
      </nav>
      <p>{t.note}</p>
    </footer>
  );
}
