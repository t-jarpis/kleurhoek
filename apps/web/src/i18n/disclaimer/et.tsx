import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Estonian (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Viimati uuendatud 24. oktoobril 2026.</p>
      <p>Sellel lehel selgitame, mida tohib teha Kleurhoeki värvimispiltide ja meisterdamislehtedega, kuidas me viitame teistele veebilehtedele ja kuidas meile millestki teada anda. Kleurhoeki kasutades nõustud nende tingimustega.</p>

      <h2>Meie oma kujundused</h2>
      <p>Kõik Kleurhoeki värvimispildid, väljalõiked ja paberimudelid on tehtud spetsiaalselt Kleurhoeki jaoks. Loome need tehisintellekti abil ja kontrollime iga pildi enne selle avaldamist üle. Me ei kopeeri midagi teistelt veebilehtedelt ega raamatutest ning me ei joonista ümber tuntud tegelasi, kaubamärke ega figuure. Veebileht, nimi Kleurhoek ja piltide kogu kuuluvad Kleurhoekile.</p>
      <p>Pilte võid tasuta kasutada:</p>
      <ul>
        <li>kodus, et neid värvida, printida ning pere ja sõpradega jagada;</li>
        <li>koolis, lasteaias, klubis või raamatukogus, ka suurtes kogustes;</li>
        <li>peol, näiteks meisterdamistegevusena.</li>
      </ul>
      <p>Ilma meie kirjaliku loata ei ole lubatud: pilte müüa (üksikult, raamatukesena või allalaaditava failina), panna neid teisele veebilehele, rakendusse või sotsiaalmeediasse oma materjalina või kasutada neid toodetes või reklaamis. Lingi jagamine Kleurhoeki lehele on alati teretulnud.</p>

      <h2>Teemad tegijatelt</h2>
      <p>Lapsed otsivad sageli värvimispilte multifilmide, teemaparkide või raamatute tegelastest. Need joonistused kuuluvad nende tegijatele ja meil ei ole lubatud neid ise teha ega kopeerida. Paljud tegijad pakuvad neid aga tasuta oma veebilehtedel. Jaotises <Link href={link(base, "/themas")}>Teemad tegijatelt</Link> kogume linke nendele lehtedele. Kehtib järgmine:</p>
      <ul>
        <li>Viitame ainult tegija või õiguste omaja ametlikule veebilehele, mitte kunagi saitidele, mis kopeerivad teiste joonistusi.</li>
        <li>Me ei näita ega salvesta tegija pilte, joonistusi ega logosid. Meie saidil näed ainult meie enda kirjeldust ja linki. Erandiks on ainult juhud, kui tegija annab meile selleks kirjaliku loa, ja siis me ütleme seda ka.</li>
        <li>Kontrollime iga lingi enne avaldamist üle. Seejärel kontrollib arvutiprogramm iga päev, kas leht on veel olemas. Kui leht kaob, eemaldame lingi automaatselt. Seejuures järgime alati tegija veebilehe reegleid (robots.txt).</li>
        <li>Tegijate veebilehtede sisu eest vastutavad nad ise ja sellele kehtivad nende enda tingimused. Meil pole selle üle mingit kontrolli.</li>
      </ul>
      <p>Oled tegija ja soovid, et me mõnda linki muudaksime või selle eemaldaksime, või tahaksid meiega koostööd teha? <Link href={contact("partnership")}>Võta meiega ühendust</Link>. Teeme muudatuse viie tööpäeva jooksul.</p>

      <h2>Kaubamärgid ja nimed</h2>
      <p>Tegelaste, teemaparkide, sarjade ja kaubamärkide nimed kuuluvad nende omanikele. Kasutame neid ainult selleks, et kirjeldada, kust midagi leida. Kleurhoek ei ole nende omanikega seotud ega saa neilt sponsorlust, kui seda pole selgelt öeldud.</p>

      <h2>Partnerlingid</h2>
      <p>Mõne pildi ja teema juures mainime asju, mida saab nendega kasutada, näiteks lastekääre või värvipliiatseid. Need on partnerlingid: kui ostad midagi sellise lingi kaudu, saab Kleurhoek poelt väikese tasu. Sina maksad sama palju. Nii jäävad pildid tasuta. Partnerlingid on alati selgelt märgitud. Toote, hinna ja tarne eest vastutab pood.</p>

      <h2>Autoriõiguse rikkumisest teatamine</h2>
      <p>Arvad, et Kleurhoekis on midagi, millele sul on õigused, või et mõni link viitab kuhugi, kuhu ei peaks? Anna sellest teada <Link href={contact("copyright")}>kontaktivormi</Link> kaudu teemaga &quot;Autoriõigus&quot;. Kirjuta, millise lehega on tegu, miks sinu arvates on midagi valesti ja kuidas sinuga ühendust saada. Vastame viie tööpäeva jooksul ja kui selleks on põhjust, eemaldame selle asja uurimise ajaks.</p>

      <h2>Ohutu meisterdamine</h2>
      <p>Väljalõiked ja paberimudelid on mõeldud tegemiseks koos täiskasvanuga. Kasuta lastekääre ja laternate puhul alati LED-tuld, mitte kunagi päris küünalt. Väikesed osad ei sobi alla kolmeaastastele lastele.</p>

      <h2>Vastutus</h2>
      <p>Teeme Kleurhoeki suure hoolega, kuid me ei saa lubada, et kõik on alati vigadeta või et veebileht on alati kättesaadav. Seadusega lubatud ulatuses ei vastuta Kleurhoek kahju eest, mis tuleneb veebilehe, piltide või meie viidatud veebilehtede kasutamisest.</p>

      <h2>Privaatsus</h2>
      <p>Loendame külastusi anonüümselt: ilma küpsisteta, ilma IP-aadressideta ja ilma millegita, mida saaks sinuga seostada. Värvimiseks ega printimiseks pole kontot vaja. Kui sa selle siiski lood, hoiame alles sinu nime, e-posti aadressi ja lemmikud, et leiaksid need kõigist oma seadmetest; kontot saad igal ajal ise kustutada. Kui tellid e-kirjad, kasutame sinu aadressi ainult selleks ja tellimusest loobumine kustutab selle. Kui saadad meile sõnumi, kasutame sinu nime ja e-posti aadressi ainult sulle vastamiseks ning hoiame sõnumit kõige rohkem kaksteist kuud. Soovid, et kustutaksime sinu sõnumi varem? <Link href={contact("privacy")}>Anna meile teada</Link>.</p>

      <h2>Muudatused ja küsimused</h2>
      <p>Võime seda teavet muuta, näiteks kui Kleurhoeki lisandub midagi uut. Ülal olev kuupäev näitab, millal seda viimati uuendati. Sellele tekstile kohaldatakse Madalmaade õigust. Küsimusi? <Link href={contact()}>Võta meiega ühendust</Link>.</p>
    </>
  );
}
