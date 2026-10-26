import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Swedish (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Senast uppdaterad den 24 oktober 2026.</p>
      <p>Den här sidan förklarar vad du får göra med Kleurhoeks målarbilder och pysselark, hur vi länkar till andra webbplatser och hur du kan rapportera något till oss. Genom att använda Kleurhoek godkänner du de här villkoren.</p>

      <h2>Våra egna bilder</h2>
      <p>Alla målarbilder, klippark och pappersmodeller på Kleurhoek är gjorda speciellt för Kleurhoek. Vi skapar dem med hjälp av AI och kontrollerar varje bild innan den publiceras. Vi kopierar ingenting från andra webbplatser eller från böcker, och vi återskapar inga kända figurer, varumärken eller karaktärer. Webbplatsen, namnet Kleurhoek och samlingen av bilder tillhör Kleurhoek.</p>
      <p>Du får använda bilderna gratis:</p>
      <ul>
        <li>hemma, för att färglägga, skriva ut och dela ut till familj och vänner;</li>
        <li>i skolan, på förskolan, i en förening eller på biblioteket, även i stora mängder;</li>
        <li>på ett kalas, till exempel som pysselaktivitet.</li>
      </ul>
      <p>Följande är inte tillåtet utan vårt skriftliga tillstånd: att sälja bilderna (var för sig, i ett häfte eller som nedladdning), att lägga upp dem på en annan webbplats, i en app eller i sociala medier som ditt eget material, eller att använda dem i produkter eller reklam. Du får gärna dela en länk till sidan på Kleurhoek.</p>

      <h2>Teman hos skaparna</h2>
      <p>Barn letar ofta efter målarbilder av figurer från en tecknad serie, en nöjespark eller en bok. De teckningarna tillhör sina skapare, och vi får inte själva göra eller kopiera dem. Men många skapare erbjuder dem gratis på sina egna webbplatser. Under <Link href={link(base, "/themas")}>Teman hos skaparna</Link> samlar vi länkar till de sidorna. Följande gäller:</p>
      <ul>
        <li>Vi länkar bara till skaparens eller rättighetsinnehavarens officiella webbplats, aldrig till webbplatser som kopierar andras teckningar.</li>
        <li>Vi visar eller sparar inga bilder, teckningar eller logotyper från skaparen. Det enda du ser på vår webbplats är vår egen beskrivning och en länk. Detta kan bara vara annorlunda om en skapare ger oss skriftligt tillstånd, och då säger vi det.</li>
        <li>Vi kontrollerar varje länk innan den publiceras. Därefter kontrollerar ett datorprogram varje dag att sidan fortfarande finns. Om en sida försvinner tar vi bort länken automatiskt. Då följer vi alltid reglerna (robots.txt) på skaparens webbplats.</li>
        <li>Innehållet på skaparnas webbplatser är deras eget ansvar och omfattas av deras egna villkor. Vi har ingen kontroll över det.</li>
      </ul>
      <p>Är du en skapare och vill att vi ändrar eller tar bort en länk, eller vill du samarbeta med oss? <Link href={contact("partnership")}>Hör av dig till oss</Link>. Vi gör ändringen inom fem arbetsdagar.</p>

      <h2>Varumärken och namn</h2>
      <p>Namn på figurer, nöjesparker, serier och varumärken tillhör sina ägare. Vi använder dem bara för att beskriva var du kan hitta något. Kleurhoek är inte knutet till dessa ägare och sponsras inte av dem, om inte det uttryckligen anges.</p>

      <h2>Partnerlänkar</h2>
      <p>Vid vissa bilder och teman nämner vi saker som du kan använda till dem, till exempel barnsaxar eller färgpennor. Det är partnerlänkar: om du köper något via en sådan länk får Kleurhoek en liten ersättning från butiken. Du betalar samma pris. Så håller vi bilderna gratis. Partnerlänkar är alltid tydligt märkta. Butiken ansvarar för produkten, priset och leveransen.</p>

      <h2>Rapportera upphovsrätt</h2>
      <p>Tror du att det finns något på Kleurhoek som du har rättigheterna till, eller att en länk pekar på något den inte borde? Rapportera det via <Link href={contact("copyright")}>kontaktformuläret</Link> med ämnet &quot;Upphovsrätt&quot;. Berätta vilken sida det gäller, varför du tycker att det inte stämmer och hur vi kan nå dig. Vi svarar inom fem arbetsdagar och tar, om det finns anledning, bort det medan vi undersöker saken.</p>

      <h2>Pyssla säkert</h2>
      <p>Klippark och pappersmodeller är tänkta att göras tillsammans med en vuxen. Använd en barnsax och använd alltid en LED-lampa i lyktor, aldrig ett riktigt ljus. Små delar är inte lämpliga för barn under tre år.</p>

      <h2>Ansvar</h2>
      <p>Vi gör Kleurhoek med stor omsorg, men vi kan inte lova att allt alltid är felfritt eller att webbplatsen alltid är tillgänglig. I den utsträckning lagen tillåter ansvarar Kleurhoek inte för skador som uppstår genom användning av webbplatsen, bilderna eller de webbplatser vi länkar till.</p>

      <h2>Integritet</h2>
      <p>Vi räknar besök anonymt: utan cookies, utan IP-adresser och utan något som kan spåras tillbaka till dig. Du behöver inget konto för att färglägga eller skriva ut. Om du ändå skapar ett sparar vi ditt namn, din e-postadress och dina favoriter, så att du hittar dem på alla dina enheter; du kan själv radera ditt konto när som helst. Om du anmäler dig till mejl använder vi din adress bara till det, och när du avregistrerar dig raderas den. Om du skickar ett meddelande till oss använder vi bara ditt namn och din e-postadress för att svara dig, och vi sparar meddelandet i högst tolv månader. Vill du att vi raderar ditt meddelande tidigare? <Link href={contact("privacy")}>Säg till</Link>.</p>

      <h2>Ändringar och frågor</h2>
      <p>Vi kan ändra den här ansvarsfriskrivningen, till exempel när något nytt läggs till på Kleurhoek. Datumet högst upp visar när den senast uppdaterades. Nederländsk lag gäller för denna ansvarsfriskrivning. Frågor? <Link href={contact()}>Hör av dig till oss</Link>.</p>
    </>
  );
}
