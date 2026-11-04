import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Sist oppdatert 4. november 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be og www.kleurhoek.com) er et nettsted med egne fargeleggingsark og formingsark for barn. Vi samler inn så lite som mulig. På denne siden står det nøyaktig hva vi faktisk lagrer, hvorfor, hvor lenge og hvilke rettigheter du har.</p>

      <h2>Hvem vi er</h2>
      <p>Kleurhoek er et nederlandsk nettsted. Har du spørsmål om personvern, kan du bruke <Link href={contact("privacy")}>kontaktskjemaet</Link> vårt.</p>

      <h2>Besøke og fargelegge</h2>
      <p>Vi teller besøk anonymt: uten informasjonskapsler, uten IP-adresser og uten noe som kan spores tilbake til deg. Vi bruker ingen reklame- eller sporingsskript fra andre, heller ikke fra Google, Meta eller Pinterest. Du kan fargelegge, skrive ut og fargelegge sammen uten konto. Det du fargelegger, blir værende på din egen enhet. Når dere fargelegger sammen, går strøkene via serveren vår til de andre i rommet, uten navn; når ingen har fargelagt på 30 minutter, stenges rommet. Navn du skriver inn på gavelapper, blir aldri sendt til serveren vår.</p>
      <p>For ikke å telle besøkende to ganger lager vi hver dag en kode av IP-adressen og nettleseren din, med en nøkkel som byttes hver dag; selve IP-adressen lagrer vi ikke. Etter 90 dager erstatter vi koden med en tilfeldig, slik at ikke engang vi kan knytte en telling til en enhet lenger. Selve tellingene (hvilken side, hvilket land, mobil eller datamaskin, når) beholder vi, slik at vi kan se hvordan nettstedet brukes gjennom årene.</p>

      <h2>Konto</h2>
      <p>Kontoer er bare for voksne (16 år eller eldre). Barn trenger ingen konto og kan ikke opprette en. Har du en konto, lagrer vi navnet ditt, e-postadressen din og favorittene dine, slik at du finner dem igjen på alle enhetene dine. Du kan slette kontoen selv; da slettes også favorittene dine og påmeldingen din til e-post.</p>

      <h2>E-post</h2>
      <p>Melder du deg på e-postene våre, lagrer vi e-postadressen din, emnene du velger og landet og språket ditt. Du bekrefter først påmeldingen via en lenke. E-postene våre inneholder ingen sporingspiksler eller omdirigerte lenker for å måle om du åpner dem. Du kan melde deg av med ett klikk nederst i hver e-post, og da sletter vi adressen din.</p>

      <h2>Kontakt</h2>
      <p>Sender du oss en melding, bruker vi navnet og e-postadressen din bare til å svare deg. Vi oppbevarer meldingen i høyst tolv måneder.</p>

      <h2>Pinterest, Facebook og Instagram</h2>
      <p>Kleurhoek publiserer egne fargeleggingsark på Kleurhoeks egne kontoer på Pinterest, Facebook og Instagram. For å gjøre det kobler vi kontoene til via den offisielle innloggingen (OAuth) fra Pinterest og Meta. Tilgangsnøklene for koblingen lagrer vi kryptert, og vi bruker dem bare til å publisere innlegg og opprette tavler på våre egne kontoer. Vi leser, samler inn eller lagrer ingen opplysninger om andre brukere av disse tjenestene, og vi bruker ikke koblingen til reklame. Knappen «Lagre på Pinterest» på nettstedet vårt er en vanlig lenke: Ingen skript fra Pinterest lastes inn. Koblingen kan fjernes når som helst, og deretter sletter vi nøklene.</p>

      <h2>Hvem som hjelper oss</h2>
      <p>Nettstedet kjører hos Scaleway i Amsterdam. Cloudflare sørger for hastighet og sikkerhet, Zitadel for innloggingen og Brevo for utsendingen av e-postene våre. De behandler opplysninger bare på våre vegne og bare til det formålet. Klikker du på en lenke til en butikk, som Amazon, gjelder den butikkens personvernerklæring fra da av.</p>

      <h2>Dine rettigheter</h2>
      <p>Du kan spørre hvilke opplysninger vi har om deg, og få dem rettet eller slettet. <Link href={contact("privacy")}>Ta kontakt</Link> med oss for å gjøre det. Er du uenig i hvordan vi behandler opplysningene dine, kan du klage til Autoriteit Persoonsgegevens (det nederlandske datatilsynet) eller til tilsynsmyndigheten i ditt eget land.</p>

      <h2>Endringer</h2>
      <p>Endrer noe seg i hva vi lagrer, oppdaterer vi denne siden. Datoen øverst viser når den sist ble oppdatert.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Personvernerklæring", description: "Hvilke opplysninger Kleurhoek lagrer, hvorfor og hvor lenge: ingen informasjonskapsler, anonym besøkstelling og kontoer bare for voksne.", Body };
