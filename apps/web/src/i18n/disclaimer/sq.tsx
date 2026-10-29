import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Albanees (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Përditësuar më 24 tetor 2026.</p>
      <p>Kjo faqe shpjegon çfarë mund të bësh me fletët për ngjyrosje dhe fletët për punë dore të Kleurhoek, si lidhemi me faqe të tjera interneti dhe si mund të na raportosh diçka. Duke përdorur Kleurhoek, pranon këto kushte.</p>

      <h2>Dizajnet tona</h2>
      <p>Të gjitha fletët për ngjyrosje, fletët për të prerë dhe modelet prej letre në Kleurhoek janë bërë posaçërisht për Kleurhoek. I krijojmë me ndihmën e inteligjencës artificiale dhe e kontrollojmë çdo fletë para se të dalë online. Nuk kopjojmë asgjë nga faqe të tjera interneti apo nga libra dhe nuk rikrijojmë personazhe, marka apo figura të njohura. Faqja e internetit, emri Kleurhoek dhe koleksioni i fletëve i përkasin Kleurhoek.</p>
      <p>Fletët mund t&apos;i përdorësh falas:</p>
      <ul>
        <li>në shtëpi, për t&apos;i ngjyrosur, printuar dhe për t&apos;ua dhënë familjes dhe miqve;</li>
        <li>në shkollë, në kopsht, në një klub ose në bibliotekë, edhe në sasi të mëdha;</li>
        <li>në një festë, për shembull si aktivitet pune dore.</li>
      </ul>
      <p>Pa lejen tonë me shkrim nuk lejohet: shitja e fletëve (një nga një, në librth ose si shkarkim), vendosja e tyre në një faqe tjetër interneti, në një aplikacion ose në rrjetet sociale si material yti, ose përdorimi i tyre në produkte apo reklama. Je i mirëpritur të ndash një lidhje drejt faqes në Kleurhoek.</p>

      <h2>Tema nga krijuesit</h2>
      <p>Fëmijët shpesh kërkojnë fletë për ngjyrosje me personazhe nga një film vizatimor, një park argëtimi apo një libër. Ato vizatime u përkasin krijuesve të tyre dhe ne nuk na lejohet t&apos;i bëjmë apo t&apos;i kopjojmë vetë. Por shumë krijues i ofrojnë falas në faqet e tyre të internetit. Te <Link href={link(base, "/themas")}>Tema nga krijuesit</Link> mbledhim lidhje drejt atyre faqeve. Vlen sa vijon:</p>
      <ul>
        <li>Lidhemi vetëm me faqen zyrtare të krijuesit ose të mbajtësit të të drejtave, kurrë me faqe që kopjojnë vizatimet e të tjerëve.</li>
        <li>Nuk shfaqim dhe nuk ruajmë imazhe, vizatime apo logo të krijuesit. Në faqen tonë sheh vetëm përshkrimin tonë dhe një lidhje. Kjo mund të jetë ndryshe vetëm nëse një krijues na jep leje me shkrim, dhe atëherë e themi.</li>
        <li>E kontrollojmë çdo lidhje para se të dalë online. Pas kësaj, një program kompjuterik kontrollon çdo ditë nëse faqja ekziston ende. Nëse një faqe zhduket, e heqim lidhjen automatikisht. Gjatë kësaj respektojmë gjithmonë rregullat (robots.txt) e faqes së krijuesit.</li>
        <li>Përmbajtja e faqeve të krijuesve është përgjegjësi e tyre dhe i nënshtrohet kushteve të tyre. Ne nuk kemi asnjë kontroll mbi të.</li>
      </ul>
      <p>Je krijues dhe dëshiron që të ndryshojmë ose të heqim një lidhje, apo dëshiron të bashkëpunosh me ne? <Link href={contact("partnership")}>Na kontakto</Link>. Do ta bëjmë ndryshimin brenda pesë ditësh pune.</p>

      <h2>Marka dhe emra</h2>
      <p>Emrat e personazheve, parqeve të argëtimit, serialeve dhe markave u përkasin pronarëve të tyre. I përdorim vetëm për të përshkruar ku mund ta gjesh diçka. Kleurhoek nuk është i lidhur me këta pronarë dhe nuk sponsorizohet prej tyre, përveç rasteve kur kjo thuhet shprehimisht.</p>

      <h2>Lidhje partnerësh</h2>
      <p>Te disa fletë dhe tema përmendim gjëra që mund t&apos;i përdorësh bashkë me to, si gërshërë për fëmijë ose lapsa me ngjyra. Këto janë lidhje partnerësh: nëse blen diçka përmes një lidhjeje të tillë, Kleurhoek merr një tarifë të vogël nga dyqani. Ti paguan njësoj. Kështu i mbajmë fletët falas. Lidhjet e partnerëve janë gjithmonë të shënuara qartë. Për produktin, çmimin dhe dorëzimin përgjigjet dyqani.</p>

      <h2>Raportimi i të drejtës së autorit</h2>
      <p>Mendon se në Kleurhoek ka diçka mbi të cilën ke të drejta, ose se një lidhje të çon diku ku nuk duhet? Raportoje përmes <Link href={contact("copyright")}>formularit të kontaktit</Link> me temën „E drejta e autorit”. Na trego për cilën faqe bëhet fjalë, pse mendon se nuk është në rregull dhe si mund të të kontaktojmë. Do të përgjigjemi brenda pesë ditësh pune dhe, nëse ka arsye, do ta heqim ndërkohë që e shqyrtojmë.</p>

      <h2>Punë dore në mënyrë të sigurt</h2>
      <p>Fletët për të prerë dhe modelet prej letre janë menduar për t&apos;u bërë bashkë me një të rritur. Përdor gërshërë për fëmijë dhe për fenerët përdor gjithmonë një dritë LED, kurrë një qiri të vërtetë. Pjesët e vogla nuk janë të përshtatshme për fëmijë nën tre vjeç.</p>

      <h2>Përgjegjësia</h2>
      <p>Kleurhoek e bëjmë me shumë kujdes, por nuk mund të premtojmë se gjithçka është gjithmonë pa gabime ose se faqja është gjithmonë e disponueshme. Për aq sa e lejon ligji, Kleurhoek nuk mban përgjegjësi për asnjë dëm që vjen nga përdorimi i faqes, i fletëve apo i faqeve me të cilat lidhemi.</p>

      <h2>Privatësia</h2>
      <p>Vizitat i numërojmë në mënyrë anonime: pa cookies, pa adresa IP dhe pa asgjë që mund të lidhet me ty. Nuk të duhet llogari për të ngjyrosur ose printuar. Nëse krijon një të tillë, ruajmë emrin tënd, adresën tënde të emailit dhe të preferuarat e tua, që t&apos;i gjesh në të gjitha pajisjet; llogarinë mund ta fshish vetë në çdo kohë. Nëse regjistrohesh për email-e, adresën tënde e përdorim vetëm për to dhe çregjistrimi e fshin atë. Nëse na dërgon një mesazh, emrin dhe adresën tënde të emailit i përdorim vetëm për të të përgjigjur dhe mesazhin e ruajmë jo më shumë se dymbëdhjetë muaj. Dëshiron ta fshijmë mesazhin tënd më herët? <Link href={contact("privacy")}>Na njofto</Link>.</p>

      <h2>Ndryshime dhe pyetje</h2>
      <p>Mund ta ndryshojmë këtë mohim përgjegjësie, për shembull kur në Kleurhoek shtohet diçka e re. Data në krye tregon kur është përditësuar për herë të fundit. Ky mohim përgjegjësie rregullohet nga ligji holandez. Ke pyetje? <Link href={contact()}>Na kontakto</Link>.</p>
    </>
  );
}
