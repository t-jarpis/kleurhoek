import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Danish (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Sidst opdateret den 24. oktober 2026.</p>
      <p>Denne side forklarer, hvad du må med Kleurhoeks tegninger til farvelægning og kreative ark, hvordan vi linker til andre hjemmesider, og hvordan du kan melde noget til os. Ved at bruge Kleurhoek accepterer du disse vilkår.</p>

      <h2>Vores egne tegninger</h2>
      <p>Alle tegninger til farvelægning, klippeark og papirmodeller på Kleurhoek er lavet specielt til Kleurhoek. Vi laver dem med hjælp fra AI og tjekker hver tegning, før den kommer online. Vi kopierer ikke noget fra andre hjemmesider eller fra bøger, og vi genskaber ikke kendte figurer, mærker eller personer. Hjemmesiden, navnet Kleurhoek og samlingen af tegninger tilhører Kleurhoek.</p>
      <p>Du må bruge tegningerne gratis:</p>
      <ul>
        <li>derhjemme, til at farvelægge, printe og dele ud til familie og venner;</li>
        <li>i skolen, i børnehaven, i en forening eller på biblioteket, også i store mængder;</li>
        <li>til en fest, for eksempel som kreativ aktivitet.</li>
      </ul>
      <p>Følgende er ikke tilladt uden vores skriftlige tilladelse: at sælge tegningerne (enkeltvis, i et hæfte eller som download), at lægge dem på en anden hjemmeside, i en app eller på sociale medier som dit eget materiale, eller at bruge dem i produkter eller reklame. Du er meget velkommen til at dele et link til siden på Kleurhoek.</p>

      <h2>Temaer hos skaberne</h2>
      <p>Børn leder ofte efter tegninger til farvelægning af figurer fra en tegnefilm, en forlystelsespark eller en bog. De tegninger tilhører deres skabere, og vi må ikke selv lave eller kopiere dem. Men mange skabere tilbyder dem gratis på deres egne hjemmesider. Under <Link href={link(base, "/themas")}>Temaer hos skaberne</Link> samler vi links til de sider. Følgende gælder:</p>
      <ul>
        <li>Vi linker kun til skaberens eller rettighedshaverens officielle hjemmeside, aldrig til sider, der kopierer andres tegninger.</li>
        <li>Vi viser eller gemmer ingen billeder, tegninger eller logoer fra skaberen. Det eneste, du ser på vores side, er vores egen beskrivelse og et link. Det kan kun være anderledes, hvis en skaber giver os skriftlig tilladelse, og i så fald skriver vi det.</li>
        <li>Vi tjekker hvert link, før det kommer online. Derefter tjekker et computerprogram hver dag, om siden stadig findes. Hvis en side forsvinder, fjerner vi linket automatisk. Her følger vi altid reglerne (robots.txt) på skaberens hjemmeside.</li>
        <li>Indholdet på skabernes hjemmesider er deres eget ansvar og er underlagt deres egne vilkår. Vi har ingen indflydelse på det.</li>
      </ul>
      <p>Er du skaber og vil have os til at ændre eller fjerne et link, eller vil du samarbejde med os? <Link href={contact("partnership")}>Kontakt os</Link>. Vi foretager ændringen inden for fem hverdage.</p>

      <h2>Mærker og navne</h2>
      <p>Navne på figurer, forlystelsesparker, serier og mærker tilhører deres ejere. Vi bruger dem kun til at beskrive, hvor du kan finde noget. Kleurhoek er ikke tilknyttet disse ejere og er ikke sponsoreret af dem, medmindre det udtrykkeligt er angivet.</p>

      <h2>Partnerlinks</h2>
      <p>Ved nogle tegninger og temaer nævner vi ting, du kan bruge til dem, for eksempel børnesakse eller farveblyanter. Det er partnerlinks: Hvis du køber noget via sådan et link, får Kleurhoek et lille beløb fra butikken. Du betaler det samme. Sådan holder vi tegningerne gratis. Partnerlinks er altid tydeligt markeret. Butikken er ansvarlig for produktet, prisen og leveringen.</p>

      <h2>Meld ophavsret</h2>
      <p>Mener du, at der er noget på Kleurhoek, som du har rettighederne til, eller at et link fører til noget, det ikke burde? Meld det via <Link href={contact("copyright")}>kontaktformularen</Link> med emnet &quot;Ophavsret&quot;. Fortæl os, hvilken side det drejer sig om, hvorfor du mener, at det ikke er i orden, og hvordan vi kan kontakte dig. Vi svarer inden for fem hverdage og fjerner det, hvis der er grund til det, mens vi undersøger sagen.</p>

      <h2>Sikker hobby</h2>
      <p>Klippeark og papirmodeller er beregnet til at blive lavet sammen med en voksen. Brug en børnesaks, og brug altid et LED-lys i lanterner, aldrig et rigtigt stearinlys. Små dele er ikke egnet til børn under tre år.</p>

      <h2>Ansvar</h2>
      <p>Vi laver Kleurhoek med stor omhu, men vi kan ikke love, at alt altid er fejlfrit, eller at hjemmesiden altid er tilgængelig. I det omfang loven tillader det, er Kleurhoek ikke ansvarlig for skader, der opstår ved brug af hjemmesiden, tegningerne eller de hjemmesider, vi linker til.</p>

      <h2>Privatliv</h2>
      <p>Vi tæller besøg anonymt: uden cookies, uden IP-adresser og uden noget, der kan spores tilbage til dig. Du behøver ikke en konto for at farvelægge eller printe. Hvis du alligevel opretter en, gemmer vi dit navn, din e-mailadresse og dine favoritter, så du kan finde dem på alle dine enheder; du kan til enhver tid selv slette din konto. Hvis du tilmelder dig mails, bruger vi kun din adresse til det, og når du afmelder dig, bliver den slettet. Hvis du sender os en besked, bruger vi kun dit navn og din e-mailadresse til at svare dig, og vi gemmer beskeden i højst tolv måneder. Vil du have, at vi sletter din besked tidligere? <Link href={contact("privacy")}>Giv os besked</Link>.</p>

      <h2>Ændringer og spørgsmål</h2>
      <p>Vi kan ændre denne ansvarsfraskrivelse, for eksempel når der kommer noget nyt på Kleurhoek. Datoen øverst viser, hvornår den sidst blev opdateret. Denne ansvarsfraskrivelse er underlagt nederlandsk ret. Spørgsmål? <Link href={contact()}>Kontakt os</Link>.</p>
    </>
  );
}
