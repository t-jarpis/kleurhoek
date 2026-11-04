import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Senast uppdaterad 4 november 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be och www.kleurhoek.com) är en webbplats med egna målarbilder och pysselark för barn. Vi samlar in så lite som möjligt. På den här sidan står exakt vad vi faktiskt sparar, varför, hur länge och vilka rättigheter du har.</p>

      <h2>Vilka vi är</h2>
      <p>Kleurhoek är en nederländsk webbplats. Har du frågor om integritet kan du använda vårt <Link href={contact("privacy")}>kontaktformulär</Link>.</p>

      <h2>Besöka och måla</h2>
      <p>Vi räknar besök anonymt: utan cookies, utan IP-adresser och utan något som kan spåras tillbaka till dig. Vi använder inga annons- eller spårningsskript från andra, inte heller från Google, Meta eller Pinterest. Du kan måla, skriva ut och måla tillsammans utan konto. Det du målar stannar på din egen enhet. När ni målar tillsammans går penseldragen via vår server till de andra i rummet, utan namn; efter 30 minuter utan att någon målar stängs rummet. Namn som du skriver in till presentetiketter skickas aldrig till vår server.</p>
      <p>För att inte räkna besökare två gånger skapar vi varje dag en kod utifrån din IP-adress och webbläsare, med en nyckel som byts varje dag; själva IP-adressen sparar vi inte. Efter 90 dagar ersätter vi koden med en slumpmässig, så att inte ens vi längre kan koppla en räkning till en enhet. Själva räkningarna (vilken sida, vilket land, mobil eller dator, när) sparar vi, så att vi kan se hur webbplatsen används genom åren.</p>

      <h2>Konto</h2>
      <p>Konton är bara för vuxna (16 år eller äldre). Barn behöver inget konto och kan inte skapa något. Har du ett konto sparar vi ditt namn, din e-postadress och dina favoriter, så att du hittar dem på alla dina enheter. Du kan själv radera ditt konto; då raderas även dina favoriter och din e-postprenumeration.</p>

      <h2>E-post</h2>
      <p>Om du anmäler dig till våra mejl sparar vi din e-postadress, de ämnen du väljer samt ditt land och språk. Du bekräftar först anmälan via en länk. Våra mejl innehåller inga spårningspixlar eller omdirigerade länkar för att mäta om du öppnar dem. Du kan avregistrera dig med ett klick längst ner i varje mejl, och då raderar vi din adress.</p>

      <h2>Kontakt</h2>
      <p>Om du skickar ett meddelande till oss använder vi ditt namn och din e-postadress bara för att svara dig. Vi sparar meddelandet i högst tolv månader.</p>

      <h2>Pinterest, Facebook och Instagram</h2>
      <p>Kleurhoek publicerar egna målarbilder på Kleurhoeks egna konton på Pinterest, Facebook och Instagram. För det kopplar vi kontona via den officiella inloggningen (OAuth) hos Pinterest och Meta. Åtkomstnycklarna för kopplingen sparar vi krypterade och använder dem bara för att publicera inlägg och skapa anslagstavlor på våra egna konton. Vi läser, samlar in eller sparar inga uppgifter om andra användare av de tjänsterna, och vi använder inte kopplingen för annonsering. Knappen ”Spara på Pinterest” på vår webbplats är en vanlig länk: inget skript från Pinterest laddas. Kopplingen kan tas bort när som helst, och därefter raderar vi nycklarna.</p>

      <h2>Vilka som hjälper oss</h2>
      <p>Webbplatsen körs hos Scaleway i Amsterdam. Cloudflare står för snabbhet och säkerhet, Zitadel för inloggningen och Brevo för utskicken av våra mejl. De behandlar uppgifter bara för vår räkning och bara för det syftet. Om du klickar på en länk till en butik, som Amazon, gäller från och med då den butikens integritetspolicy.</p>

      <h2>Dina rättigheter</h2>
      <p>Du får fråga vilka uppgifter vi har om dig och få dem rättade eller raderade. <Link href={contact("privacy")}>Kontakta oss</Link> i så fall. Om du inte håller med om hur vi hanterar dina uppgifter kan du lämna in ett klagomål till Autoriteit Persoonsgegevens (den nederländska dataskyddsmyndigheten) eller till myndigheten i ditt eget land.</p>

      <h2>Ändringar</h2>
      <p>Om något ändras i vad vi sparar uppdaterar vi den här sidan. Datumet högst upp visar när den senast uppdaterades.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Integritetspolicy", description: "Vilka uppgifter Kleurhoek sparar, varför och hur länge: inga cookies, anonym besöksräkning och konton bara för vuxna.", Body };
