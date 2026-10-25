import Link from "next/link";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Duits (ADR 0026). Zelfde opbouw als nl.tsx. */
export function Disclaimer({ market, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Zuletzt aktualisiert am 24. Oktober 2026.</p>
      <p>Auf dieser Seite erfährst du, was du mit den Malvorlagen und Bastelbögen von Kleurhoek machen darfst, wie wir auf andere Websites verlinken und wie du uns etwas meldest. Wenn du Kleurhoek nutzt, bist du mit diesen Regeln einverstanden.</p>

      <h2>Eigene Entwürfe</h2>
      <p>Alle Malvorlagen, Schneidebögen und Bastelbögen auf Kleurhoek sind extra für Kleurhoek gemacht. Wir erstellen sie mit Hilfe von KI und prüfen jede Vorlage, bevor sie online geht. Wir kopieren nichts von anderen Websites oder aus Büchern, und wir bilden keine bekannten Figuren, Marken oder Charaktere nach. Die Website, der Name Kleurhoek und die Sammlung der Vorlagen gehören Kleurhoek.</p>
      <p>Du darfst die Vorlagen kostenlos nutzen:</p>
      <ul>
        <li>zu Hause, zum Ausmalen, Ausdrucken und Verschenken an Familie und Freunde;</li>
        <li>in der Schule, in der Kita, im Verein oder in der Bibliothek, auch in großer Zahl;</li>
        <li>auf einer Feier, zum Beispiel als Bastelaktion.</li>
      </ul>
      <p>Ohne unsere schriftliche Erlaubnis ist Folgendes nicht erlaubt: Vorlagen verkaufen (einzeln, in einem Heft oder als Download), sie als eigenes Material auf einer anderen Website, in einer App oder in sozialen Medien veröffentlichen oder sie in Produkten oder in der Werbung verwenden. Teilen ist erlaubt, mit einem Link zur Vorlage auf Kleurhoek.</p>

      <h2>Themen bei den Machern</h2>
      <p>Kinder suchen oft Malvorlagen von Figuren aus einem Zeichentrickfilm, einem Freizeitpark oder einem Buch. Diese Zeichnungen gehören den Machern, und wir dürfen sie nicht selbst zeichnen oder kopieren. Viele Macher bieten sie aber kostenlos auf ihrer eigenen Website an. Unter <Link href={`/${market}/themas`}>Themen bei den Machern</Link> sammeln wir Links zu diesen Seiten. Dabei gilt:</p>
      <ul>
        <li>Wir verlinken nur auf die offizielle Website des Machers oder Rechteinhabers, nie auf Seiten, die Zeichnungen anderer übernehmen.</li>
        <li>Wir zeigen keine Bilder, Zeichnungen oder Logos der Macher und speichern sie auch nicht. Bei uns siehst du nur eine eigene Beschreibung und einen Link. Nur wenn ein Macher uns dazu schriftlich die Erlaubnis gibt, kann das anders sein; das steht dann dabei.</li>
        <li>Jeden Link sehen wir uns an, bevor er online geht. Danach prüft ein Computerprogramm jeden Tag, ob die Seite noch existiert. Verschwindet eine Seite, entfernen wir den Link automatisch. Dabei halten wir uns immer an die Regeln (robots.txt) der Website des Machers.</li>
        <li>Für die Inhalte der Websites der Macher sind diese selbst verantwortlich; es gelten ihre eigenen Bedingungen. Darauf haben wir keinen Einfluss.</li>
      </ul>
      <p>Bist du ein Macher und möchtest, dass wir einen Link ändern oder entfernen, oder möchtest du mit uns zusammenarbeiten? <Link href={contact("partnership")}>Nimm Kontakt mit uns auf</Link>. Wir ändern es innerhalb von fünf Werktagen.</p>

      <h2>Marken und Namen</h2>
      <p>Namen von Figuren, Freizeitparks, Serien und Marken gehören ihren Inhabern. Wir verwenden sie nur, um zu beschreiben, wo du etwas finden kannst. Kleurhoek ist nicht mit diesen Inhabern verbunden und wird nicht von ihnen gesponsert, es sei denn, das steht ausdrücklich dabei.</p>

      <h2>Partnerlinks</h2>
      <p>Bei manchen Vorlagen und Themen nennen wir Sachen, die du dazu verwenden kannst, zum Beispiel eine Kinderschere oder Buntstifte. Das sind Partnerlinks: Wenn du über so einen Link etwas kaufst, bekommt Kleurhoek eine kleine Vergütung vom Shop. Du zahlst dasselbe. So bleiben die Vorlagen kostenlos. Partnerlinks sind immer deutlich gekennzeichnet. Für das Produkt, den Preis und die Lieferung ist der Shop verantwortlich.</p>

      <h2>Urheberrechtsverletzung melden</h2>
      <p>Glaubst du, dass auf Kleurhoek etwas steht, an dem du die Rechte hast, oder dass ein Link auf etwas verweist, das nicht erlaubt sein sollte? Melde es über das <Link href={contact("copyright")}>Kontaktformular</Link> mit dem Thema &quot;Urheberrecht&quot;. Gib an, um welche Seite es geht, warum es deiner Meinung nach nicht in Ordnung ist und wie wir dich erreichen können. Wir antworten innerhalb von fünf Werktagen und entfernen den Inhalt, solange wir die Sache prüfen, wenn es dafür einen Grund gibt.</p>

      <h2>Sicher basteln</h2>
      <p>Schneide- und Bastelbögen sind dafür gedacht, sie gemeinsam mit einem Erwachsenen zu machen. Verwende eine Kinderschere und bei Laternen immer ein LED-Licht und nie eine echte Kerze. Kleine Teile sind nicht für Kinder unter drei Jahren geeignet.</p>

      <h2>Haftung</h2>
      <p>Wir machen Kleurhoek mit viel Sorgfalt, aber wir können nicht versprechen, dass alles immer fehlerfrei ist oder dass die Website immer erreichbar ist. Soweit gesetzlich zulässig, haftet Kleurhoek nicht für Schäden, die durch die Nutzung der Website, der Vorlagen oder der Websites entstehen, auf die wir verlinken.</p>

      <h2>Datenschutz</h2>
      <p>Wir zählen Besuche anonym: ohne Cookies, ohne IP-Adresse und ohne etwas, das sich auf dich zurückführen lässt. Zum Ausmalen und Drucken brauchst du kein Konto. Legst du doch eins an, speichern wir deinen Namen, deine E-Mail-Adresse und deine Favoriten, damit du sie auf all deinen Geräten wiederfindest; dein Konto kannst du jederzeit selbst löschen. Meldest du dich für E-Mails an, nutzen wir deine Adresse nur dafür, und Abmelden löscht sie. Wenn du uns eine Nachricht schickst, verwenden wir deinen Namen und deine E-Mail-Adresse nur, um dir zu antworten, und speichern die Nachricht höchstens zwölf Monate. Möchtest du, dass wir deine Nachricht früher löschen? <Link href={contact("privacy")}>Sag uns Bescheid</Link>.</p>

      <h2>Änderungen und Fragen</h2>
      <p>Wir können diesen Haftungsausschluss ändern, zum Beispiel wenn es etwas Neues auf Kleurhoek gibt. Oben steht, wann er zuletzt aktualisiert wurde. Für diesen Haftungsausschluss gilt niederländisches Recht. Fragen? <Link href={contact()}>Nimm Kontakt mit uns auf</Link>.</p>
    </>
  );
}
