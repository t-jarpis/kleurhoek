import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Senest opdateret 4. november 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be og www.kleurhoek.com) er en hjemmeside med egne malebilleder og klippe-klistre-ark til børn. Vi indsamler så lidt som muligt. På denne side står der præcis, hvad vi gemmer, hvorfor, hvor længe, og hvilke rettigheder du har.</p>

      <h2>Hvem vi er</h2>
      <p>Kleurhoek er en hollandsk hjemmeside. Har du spørgsmål om privatliv, så brug vores <Link href={contact("privacy")}>kontaktformular</Link>.</p>

      <h2>Besøg og farvelægning</h2>
      <p>Vi tæller besøg anonymt: uden cookies, uden IP-adresser og uden noget, der kan spores tilbage til dig. Vi bruger ingen reklame- eller sporingsscripts fra andre, heller ikke fra Google, Meta eller Pinterest. Du kan farvelægge, printe og farvelægge sammen uden en konto. Det, du farvelægger, bliver på din egen enhed. Når I farvelægger sammen, går strøgene via vores server til de andre i rummet, uden navne; når ingen har farvelagt i 30 minutter, lukker rummet. Navne, du skriver til gavemærkater, bliver aldrig sendt til vores server.</p>
      <p>For ikke at tælle besøgende to gange laver vi hver dag en kode ud fra din IP-adresse og din browser med en nøgle, der skifter hver dag; selve IP-adressen gemmer vi ikke. Efter 90 dage erstatter vi koden med en tilfældig, så ikke engang vi længere kan koble en optælling til en enhed. Selve optællingerne (hvilken side, hvilket land, telefon eller computer, hvornår) gemmer vi, så vi kan se, hvordan siden bliver brugt gennem årene.</p>

      <h2>Konto</h2>
      <p>Konti er kun for voksne (16 år eller ældre). Børn har ikke brug for en konto og kan ikke oprette en. Har du en konto, gemmer vi dit navn, din e-mailadresse og dine favoritter, så du kan finde dem på alle dine enheder. Du kan selv slette din konto; så bliver dine favoritter og din tilmelding til e-mails også slettet.</p>

      <h2>E-mail</h2>
      <p>Tilmelder du dig vores e-mails, gemmer vi din e-mailadresse, de emner, du vælger, og dit land og sprog. Du bekræfter først tilmeldingen via et link. Vores e-mails indeholder ingen sporingspixels eller omdirigerede links til at måle, om du åbner dem. Du kan afmelde dig med ét klik nederst i hver e-mail, og så sletter vi din adresse.</p>

      <h2>Kontakt</h2>
      <p>Sender du os en besked, bruger vi kun dit navn og din e-mailadresse til at svare dig. Vi gemmer beskeden i højst tolv måneder.</p>

      <h2>Pinterest, Facebook og Instagram</h2>
      <p>Kleurhoek udgiver sine egne malebilleder på Kleurhoeks egne konti på Pinterest, Facebook og Instagram. Det gør vi ved at forbinde kontiene via det officielle login (OAuth) fra Pinterest og Meta. Adgangsnøglerne til forbindelsen gemmer vi krypteret, og vi bruger dem kun til at udgive opslag og oprette opslagstavler på vores egne konti. Vi læser, indsamler eller gemmer ingen data om andre brugere af de tjenester, og vi bruger ikke forbindelsen til reklame. Knappen »Gem på Pinterest« på vores side er et almindeligt link: der indlæses intet script fra Pinterest. Forbindelsen kan til enhver tid fjernes, hvorefter vi sletter nøglerne.</p>

      <h2>Hvem hjælper os</h2>
      <p>Hjemmesiden kører hos Scaleway i Amsterdam. Cloudflare sørger for hastighed og sikkerhed, Zitadel for login og Brevo for at sende vores e-mails. De behandler kun data på vores vegne og kun til det formål. Klikker du på et link til en butik, som Amazon, gælder den butiks privatlivspolitik fra det øjeblik.</p>

      <h2>Dine rettigheder</h2>
      <p>Du må spørge, hvilke data vi har om dig, og få dem rettet eller slettet. <Link href={contact("privacy")}>Kontakt os</Link> for at gøre det. Er du uenig i, hvordan vi behandler dine data, kan du klage til Autoriteit Persoonsgegevens (den hollandske databeskyttelsesmyndighed) eller til myndigheden i dit eget land.</p>

      <h2>Ændringer</h2>
      <p>Ændrer der sig noget i det, vi gemmer, opdaterer vi denne side. Datoen øverst viser, hvornår den sidst blev opdateret.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Privatlivspolitik", description: "Hvilke data Kleurhoek gemmer, hvorfor og hvor længe: ingen cookies, anonym optælling af besøg og konti kun for voksne.", Body };
