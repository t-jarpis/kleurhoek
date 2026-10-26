import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Norwegian Bokmål (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Sist oppdatert 24. oktober 2026.</p>
      <p>Denne siden forklarer hva du kan gjøre med Kleurhoeks fargeleggingsark og hobbyark, hvordan vi lenker til andre nettsider og hvordan du kan melde fra om noe til oss. Ved å bruke Kleurhoek godtar du disse vilkårene.</p>

      <h2>Våre egne ark</h2>
      <p>Alle fargeleggingsark, klippeark og papirmodeller på Kleurhoek er laget spesielt for Kleurhoek. Vi lager dem med hjelp av KI og sjekker hvert ark før det publiseres. Vi kopierer ingenting fra andre nettsider eller fra bøker, og vi gjenskaper ikke kjente figurer, merkevarer eller personer. Nettsiden, navnet Kleurhoek og samlingen av ark tilhører Kleurhoek.</p>
      <p>Du kan bruke arkene gratis:</p>
      <ul>
        <li>hjemme, til å fargelegge, skrive ut og dele ut til familie og venner;</li>
        <li>på skolen, i barnehagen, i en forening eller på biblioteket, også i store mengder;</li>
        <li>på en fest, for eksempel som hobbyaktivitet.</li>
      </ul>
      <p>Følgende er ikke tillatt uten vår skriftlige tillatelse: å selge arkene (enkeltvis, i et hefte eller som nedlasting), å legge dem ut på en annen nettside, i en app eller i sosiale medier som ditt eget materiale, eller å bruke dem i produkter eller reklame. Du er velkommen til å dele en lenke til siden på Kleurhoek.</p>

      <h2>Temaer hos skaperne</h2>
      <p>Barn leter ofte etter fargeleggingsark av figurer fra en tegnefilm, en fornøyelsespark eller en bok. Disse tegningene tilhører skaperne, og vi har ikke lov til å lage eller kopiere dem selv. Men mange skapere tilbyr dem gratis på sine egne nettsider. Under <Link href={link(base, "/themas")}>Temaer hos skaperne</Link> samler vi lenker til disse sidene. Følgende gjelder:</p>
      <ul>
        <li>Vi lenker bare til den offisielle nettsiden til skaperen eller rettighetshaveren, aldri til nettsider som kopierer andres tegninger.</li>
        <li>Vi viser eller lagrer ingen bilder, tegninger eller logoer fra skaperen. Det eneste du ser på nettsiden vår, er vår egen beskrivelse og en lenke. Dette kan bare være annerledes hvis en skaper gir oss skriftlig tillatelse, og da sier vi det.</li>
        <li>Vi sjekker hver lenke før den publiseres. Deretter sjekker et dataprogram hver dag om siden fortsatt finnes. Hvis en side forsvinner, fjerner vi lenken automatisk. Vi følger alltid reglene (robots.txt) på skaperens nettside.</li>
        <li>Innholdet på skapernes nettsider er deres eget ansvar og er underlagt deres egne vilkår. Vi har ingen kontroll over det.</li>
      </ul>
      <p>Er du skaper og vil at vi skal endre eller fjerne en lenke, eller vil du samarbeide med oss? <Link href={contact("partnership")}>Ta kontakt med oss</Link>. Vi gjør endringen innen fem virkedager.</p>

      <h2>Merkevarer og navn</h2>
      <p>Navn på figurer, fornøyelsesparker, serier og merkevarer tilhører eierne sine. Vi bruker dem bare for å beskrive hvor du kan finne noe. Kleurhoek er ikke tilknyttet disse eierne og er ikke sponset av dem, med mindre det uttrykkelig står.</p>

      <h2>Partnerlenker</h2>
      <p>Ved noen ark og temaer nevner vi ting du kan bruke til dem, for eksempel barnesakser eller fargeblyanter. Dette er partnerlenker: Hvis du kjøper noe via en slik lenke, får Kleurhoek en liten provisjon fra butikken. Du betaler det samme. Slik holder vi arkene gratis. Partnerlenker er alltid tydelig merket. Butikken er ansvarlig for produktet, prisen og leveringen.</p>

      <h2>Melde fra om opphavsrett</h2>
      <p>Mener du at det er noe på Kleurhoek som du har rettighetene til, eller at en lenke peker til noe den ikke burde? Meld fra via <Link href={contact("copyright")}>kontaktskjemaet</Link> med emnet &quot;Opphavsrett&quot;. Fortell oss hvilken side det gjelder, hvorfor du mener det ikke er riktig og hvordan vi kan nå deg. Vi svarer innen fem virkedager og fjerner det, hvis det er grunn til det, mens vi undersøker saken.</p>

      <h2>Trygg hobby</h2>
      <p>Klippeark og papirmodeller er ment å lages sammen med en voksen. Bruk en barnesaks, og bruk alltid et LED-lys i lykter, aldri et ekte stearinlys. Små deler er ikke egnet for barn under tre år.</p>

      <h2>Ansvar</h2>
      <p>Vi lager Kleurhoek med stor omhu, men vi kan ikke love at alt alltid er feilfritt eller at nettsiden alltid er tilgjengelig. Så langt loven tillater det, er Kleurhoek ikke ansvarlig for skade som oppstår ved bruk av nettsiden, arkene eller nettsidene vi lenker til.</p>

      <h2>Personvern</h2>
      <p>Vi teller besøk anonymt: uten informasjonskapsler, uten IP-adresser og uten noe som kan spores tilbake til deg. Du trenger ikke en konto for å fargelegge eller skrive ut. Hvis du likevel oppretter en, lagrer vi navnet ditt, e-postadressen din og favorittene dine, slik at du finner dem på alle enhetene dine; du kan selv slette kontoen din når som helst. Hvis du melder deg på e-post, bruker vi adressen din bare til det, og når du melder deg av, slettes den. Hvis du sender oss en melding, bruker vi bare navnet og e-postadressen din til å svare deg, og vi lagrer meldingen i høyst tolv måneder. Vil du at vi sletter meldingen din tidligere? <Link href={contact("privacy")}>Gi oss beskjed</Link>.</p>

      <h2>Endringer og spørsmål</h2>
      <p>Vi kan endre denne ansvarsfraskrivelsen, for eksempel når noe nytt kommer på Kleurhoek. Datoen øverst viser når den sist ble oppdatert. Denne ansvarsfraskrivelsen er underlagt nederlandsk rett. Spørsmål? <Link href={contact()}>Ta kontakt med oss</Link>.</p>
    </>
  );
}
