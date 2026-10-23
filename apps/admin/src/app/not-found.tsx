import { Logo } from "@kleurhoek/theme";
import Link from "next/link";

/** Onbekend adres in het admin panel (bijv. een pad van de website dat de browser aanvulde). */
export default function NotFound() {
  return (
    <div className="center">
      <div className="panel stack" style={{ maxWidth: 420 }}>
        <Logo suffix="beheer" size={20} />
        <h1>Pagina niet gevonden</h1>
        <p className="lead">Dit adres bestaat niet in het admin panel. Misschien was het een adres van de website?</p>
        <Link className="button" href="/">Naar het dashboard</Link>
      </div>
    </div>
  );
}
