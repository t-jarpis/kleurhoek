import Link from "next/link";
import type { Messages } from "@/i18n/nl";

/** Onderaan elke pagina: disclaimer, contact en de Bronnengids (ADR 0023, 0024). */
export function SiteFooter({ market, t }: { market: string; t: Messages }) {
  return (
    <footer className="kh-footer no-print">
      <nav aria-label="Over Kleurhoek">
        <Link href={`/${market}/themas`}>{t.themes}</Link>
        <Link href={`/${market}/contact`}>{t.contact}</Link>
        <Link href={`/${market}/disclaimer`}>{t.disclaimer}</Link>
      </nav>
      <p>{t.note}</p>
    </footer>
  );
}
