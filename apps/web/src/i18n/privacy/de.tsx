import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Zuletzt aktualisiert am 4. November 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be und www.kleurhoek.com) ist eine Website mit eigenen Ausmalbildern und Bastelvorlagen für Kinder. Wir erheben so wenig wie möglich. Auf dieser Seite steht genau, was wir doch speichern, warum, wie lange und welche Rechte du hast.</p>

      <h2>Wer wir sind</h2>
      <p>Kleurhoek ist eine niederländische Website. Für Fragen zum Datenschutz nutze bitte unser <Link href={contact("privacy")}>Kontaktformular</Link>.</p>

      <h2>Besuchen und Ausmalen</h2>
      <p>Wir zählen Besuche anonym: ohne Cookies, ohne IP-Adressen und ohne irgendetwas, das sich auf dich zurückführen lässt. Wir verwenden keine Werbe- oder Tracking-Skripte von anderen, auch nicht von Google, Meta oder Pinterest. Ausmalen, Drucken und gemeinsames Ausmalen geht ohne Konto. Was du ausmalst, bleibt auf deinem eigenen Gerät. Malt ihr gemeinsam aus, gehen die Striche ohne Namen über unseren Server an die anderen im Raum; wird 30 Minuten lang nicht ausgemalt, endet der Raum. Namen, die du für Geschenkanhänger eintippst, werden nie an unseren Server gesendet.</p>
      <p>Damit wir Besucher nicht doppelt zählen, bilden wir jeden Tag einen Code aus deiner IP-Adresse und deinem Browser, mit einem Schlüssel, der täglich wechselt; die IP-Adresse selbst speichern wir nicht. Nach 90 Tagen ersetzen wir diesen Code durch einen zufälligen, sodass nicht einmal wir eine Zählung noch einem Gerät zuordnen können. Die Zählungen selbst (welche Seite, welches Land, Handy oder Computer, wann) bewahren wir auf, damit wir sehen können, wie die Website über die Jahre genutzt wird.</p>

      <h2>Konto</h2>
      <p>Konten sind nur für Erwachsene (ab 16 Jahren). Kinder brauchen kein Konto und können keines anlegen. Wenn du ein Konto hast, speichern wir deinen Namen, deine E-Mail-Adresse und deine Favoriten, damit du sie auf all deinen Geräten wiederfindest. Du kannst dein Konto selbst löschen; deine Favoriten und deine E-Mail-Anmeldung werden dann mitgelöscht.</p>

      <h2>E-Mail</h2>
      <p>Wenn du dich für E-Mails anmeldest, speichern wir deine E-Mail-Adresse, die Themen, die du auswählst, sowie dein Land und deine Sprache. Du bestätigst die Anmeldung zuerst über einen Link. Unsere E-Mails enthalten keine Tracking-Pixel oder umgeleiteten Links, mit denen gemessen wird, ob du sie öffnest. Du kannst dich mit einem Klick unten in jeder E-Mail abmelden; dann löschen wir deine Adresse.</p>

      <h2>Kontakt</h2>
      <p>Wenn du uns eine Nachricht schickst, verwenden wir deinen Namen und deine E-Mail-Adresse nur, um dir zu antworten. Wir bewahren die Nachricht höchstens zwölf Monate auf.</p>

      <h2>Pinterest, Facebook und Instagram</h2>
      <p>Kleurhoek veröffentlicht eigene Ausmalbilder auf den eigenen Konten von Kleurhoek bei Pinterest, Facebook und Instagram. Dazu verbinden wir diese Konten über die offizielle Anmeldung (OAuth) von Pinterest und Meta. Die Zugangsschlüssel für diese Verbindung speichern wir verschlüsselt und verwenden sie nur, um Beiträge auf unseren eigenen Konten zu veröffentlichen und Pinnwände anzulegen. Wir lesen, sammeln oder speichern keine Daten anderer Nutzer dieser Dienste, und wir nutzen die Verbindung nicht für Werbung. Der Button „Auf Pinterest merken“ auf unserer Website ist ein einfacher Link: Es wird kein Skript von Pinterest geladen. Die Verbindung kann jederzeit getrennt werden; danach löschen wir die Schlüssel.</p>

      <h2>Wer uns hilft</h2>
      <p>Die Website läuft bei Scaleway in Amsterdam. Cloudflare sorgt für Geschwindigkeit und Sicherheit, Zitadel für die Anmeldung und Brevo für den Versand unserer E-Mails. Sie verarbeiten Daten nur in unserem Auftrag und nur für diesen Zweck. Wenn du auf einen Link zu einem Shop wie Amazon klickst, gilt ab dann die Datenschutzerklärung dieses Shops.</p>

      <h2>Deine Rechte</h2>
      <p>Du kannst fragen, welche Daten wir über dich haben, und sie berichtigen oder löschen lassen. Nimm dazu bitte <Link href={contact("privacy")}>Kontakt</Link> mit uns auf. Wenn du nicht einverstanden bist, wie wir mit deinen Daten umgehen, kannst du dich bei der Autoriteit Persoonsgegevens (der niederländischen Datenschutzbehörde) oder bei der Datenschutzbehörde in deinem eigenen Land beschweren.</p>

      <h2>Änderungen</h2>
      <p>Wenn sich etwas daran ändert, was wir speichern, passen wir diese Seite an. Das Datum oben zeigt, wann sie zuletzt aktualisiert wurde.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Datenschutzerklärung", description: "Welche Daten Kleurhoek speichert, warum und wie lange: keine Cookies, anonyme Besuchszählung und Konten nur für Erwachsene.", Body };
