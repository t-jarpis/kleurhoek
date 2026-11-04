import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Bijgewerkt op 4 november 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be en www.kleurhoek.com) is een website met eigen kleurplaten en knutselplaten voor kinderen. We verzamelen zo weinig mogelijk. Hieronder staat precies wat we wel bewaren, waarom, hoe lang en wat je rechten zijn.</p>

      <h2>Wie we zijn</h2>
      <p>Kleurhoek is een Nederlandse website. Voor vragen over privacy gebruik je het <Link href={contact("privacy")}>contactformulier</Link>.</p>

      <h2>Bezoeken en kleuren</h2>
      <p>We tellen bezoeken anoniem: zonder cookies, zonder IP-adressen en zonder iets wat naar jou terug te leiden is. We gebruiken geen advertentie- of trackingscripts van anderen, ook niet van Google, Meta of Pinterest. Kleuren, printen en samen kleuren kan zonder account. Wat je kleurt, blijft op je eigen apparaat. Kleur je samen, dan gaan de streken via onze server naar de anderen in de kamer, zonder namen; kleurt er 30 minuten niemand, dan stopt de kamer. Namen die je intypt voor cadeaulabels gaan niet naar onze server.</p>
      <p>Om bezoekers niet dubbel te tellen, maken we per dag een code van je IP-adres en browser, met een sleutel die elke dag wisselt; het IP-adres zelf slaan we niet op. Na 90 dagen vervangen we die code door een willekeurige, zodat ook wij een telling niet meer aan een apparaat kunnen koppelen. De tellingen zelf (welke plaat, welk land, telefoon of computer, wanneer) bewaren we, zodat we kunnen zien hoe de site door de jaren heen gebruikt wordt.</p>

      <h2>Account</h2>
      <p>Een account is alleen voor volwassenen (16 jaar of ouder). Kinderen hebben geen account nodig en kunnen er geen aanmaken. Met een account bewaren we je naam, je e-mailadres en je favorieten, zodat je ze op al je apparaten terugvindt. Je kunt je account zelf verwijderen; dan verdwijnen ook je favorieten en je aanmelding voor mail.</p>

      <h2>Mail</h2>
      <p>Meld je je aan voor mail, dan bewaren we je e-mailadres, de onderwerpen die je kiest en je land en taal. Je bevestigt de aanmelding eerst via een link. In de mails zitten geen pixels of omgeleide links om te meten of je ze opent. Afmelden kan met één klik onderaan elke mail, en dan verwijderen we je adres.</p>

      <h2>Contact</h2>
      <p>Stuur je ons een bericht, dan gebruiken we je naam en e-mailadres alleen om te antwoorden. We bewaren het bericht hooguit twaalf maanden.</p>

      <h2>Pinterest, Facebook en Instagram</h2>
      <p>Kleurhoek plaatst eigen kleurplaten op de eigen accounts van Kleurhoek bij Pinterest, Facebook en Instagram. Daarvoor koppelen we die accounts via de officiële inlog (OAuth) van Pinterest en Meta. De sleutels van die koppeling bewaren we versleuteld en gebruiken we alleen om berichten op onze eigen accounts te plaatsen en borden aan te maken. We lezen, verzamelen of bewaren geen gegevens van andere gebruikers van die diensten, en we gebruiken de koppeling niet voor advertenties. De knop "Bewaar op Pinterest" op de site is een gewone link: er wordt geen script van Pinterest geladen. De koppeling kan op elk moment worden verbroken, waarna we de sleutels verwijderen.</p>

      <h2>Wie ons helpt</h2>
      <p>De website draait bij Scaleway in Amsterdam. Cloudflare zorgt voor snelheid en beveiliging, Zitadel voor het inloggen en Brevo voor het versturen van mail. Zij verwerken gegevens alleen voor ons en alleen voor dat doel. Klik je op een link naar een winkel, zoals Amazon, dan geldt vanaf dat moment het privacybeleid van die winkel.</p>

      <h2>Je rechten</h2>
      <p>Je mag vragen welke gegevens we van je hebben, ze laten verbeteren of laten verwijderen. Neem daarvoor <Link href={contact("privacy")}>contact</Link> met ons op. Ben je het niet eens met hoe we met je gegevens omgaan, dan kun je een klacht indienen bij de Autoriteit Persoonsgegevens of bij de toezichthouder in het land waar je woont.</p>

      <h2>Wijzigingen</h2>
      <p>Verandert er iets aan wat we bewaren, dan passen we deze pagina aan. De datum bovenaan laat zien wanneer dat voor het laatst gebeurde.</p>
    </>
  );
}

export const nl: PrivacyText = { title: "Privacybeleid", description: "Welke gegevens Kleurhoek bewaart, waarom en hoe lang: geen cookies, anonieme telling, en accounts alleen voor volwassenen.", Body };
