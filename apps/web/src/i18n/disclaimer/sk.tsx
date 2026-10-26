import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Slowaaks (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Naposledy aktualizované 24. októbra 2026.</p>
      <p>Na tejto stránke sa dozviete, čo smiete robiť s omaľovánkami a vystrihovačkami Kleurhoek, ako odkazujeme na iné weby a ako nám môžete niečo nahlásiť. Používaním Kleurhoeku s týmito podmienkami súhlasíte.</p>

      <h2>Naše vlastné návrhy</h2>
      <p>Všetky omaľovánky, vystrihovačky a papierové modely na Kleurhoeku vznikli špeciálne pre Kleurhoek. Vytvárame ich s pomocou umelej inteligencie a každý obrázok pred zverejnením kontrolujeme. Nič nekopírujeme z iných webov ani z kníh a nekreslíme známe postavičky, značky ani figúrky. Web, názov Kleurhoek a zbierka obrázkov patria Kleurhoeku.</p>
      <p>Obrázky môžete používať zadarmo:</p>
      <ul>
        <li>doma, na vyfarbovanie, tlač a rozdávanie rodine a priateľom;</li>
        <li>v škole, v škôlke, v krúžku alebo v knižnici, aj vo veľkom množstve;</li>
        <li>na oslave, napríklad ako tvorivú aktivitu.</li>
      </ul>
      <p>Bez nášho písomného súhlasu nie je dovolené: obrázky predávať (jednotlivo, v zošite ani na stiahnutie), zverejňovať ich na inom webe, v aplikácii alebo na sociálnych sieťach ako vlastný materiál ani ich používať vo výrobkoch alebo v reklame. Odkaz na stránku na Kleurhoeku zdieľať môžete.</p>

      <h2>Témy od autorov</h2>
      <p>Deti často hľadajú omaľovánky s postavičkami z rozprávok, zábavných parkov alebo kníh. Tieto kresby patria ich autorom a my ich sami kresliť ani kopírovať nesmieme. Mnohí autori ich však ponúkajú zadarmo na svojich vlastných weboch. V časti <Link href={link(base, "/themas")}>Témy od autorov</Link> zbierame odkazy na tieto stránky. Platí pritom:</p>
      <ul>
        <li>Odkazujeme len na oficiálny web autora alebo držiteľa práv, nikdy na weby, ktoré kopírujú cudzie kresby.</li>
        <li>Nezobrazujeme ani neukladáme žiadne obrázky, kresby ani logá autora. Na našom webe vidíte len náš vlastný popis a odkaz. Inak to môže byť len vtedy, keď nám autor dá písomný súhlas; potom to uvádzame.</li>
        <li>Každý odkaz pred zverejnením kontrolujeme. Potom počítačový program každý deň overuje, či stránka stále existuje. Keď stránka zmizne, odkaz automaticky odstránime. Vždy pritom dodržiavame pravidlá (robots.txt) webu autora.</li>
        <li>Za obsah webov autorov zodpovedajú samotní autori a platia preň ich vlastné podmienky. Nemáme naň žiadny vplyv.</li>
      </ul>
      <p>Ste autor a chcete, aby sme odkaz upravili alebo odstránili, alebo s nami chcete spolupracovať? <Link href={contact("partnership")}>Ozvite sa nám</Link>. Zmenu urobíme do piatich pracovných dní.</p>

      <h2>Značky a názvy</h2>
      <p>Názvy postavičiek, zábavných parkov, seriálov a značiek patria ich vlastníkom. Používame ich len na opis toho, kde niečo nájdete. Kleurhoek nie je s týmito vlastníkmi spojený a nie je nimi sponzorovaný, pokiaľ to nie je výslovne uvedené.</p>

      <h2>Partnerské odkazy</h2>
      <p>Pri niektorých obrázkoch a témach spomíname veci, ktoré sa k nim hodia, napríklad detské nožnice alebo pastelky. Ide o partnerské odkazy: keď cez taký odkaz niečo kúpite, Kleurhoek dostane od obchodu malú odmenu. Vy zaplatíte rovnako. Vďaka tomu zostávajú obrázky zadarmo. Partnerské odkazy sú vždy jasne označené. Za výrobok, cenu a doručenie zodpovedá obchod.</p>

      <h2>Nahlásenie porušenia autorských práv</h2>
      <p>Myslíte si, že je na Kleurhoeku niečo, k čomu máte práva vy, alebo že odkaz vedie niekam, kam by nemal? Nahláste to cez <Link href={contact("copyright")}>kontaktný formulár</Link> s témou &quot;Autorské práva&quot;. Uveďte, o ktorú stránku ide, prečo si myslíte, že to nie je v poriadku, a ako vás môžeme kontaktovať. Odpovieme do piatich pracovných dní a ak na to bude dôvod, obsah počas preverovania odstránime.</p>

      <h2>Bezpečné tvorenie</h2>
      <p>Vystrihovačky a papierové modely sú určené na tvorenie spolu s dospelým. Používajte detské nožnice a do lampiónov vždy dávajte LED svetlo, nikdy skutočnú sviečku. Malé diely nie sú vhodné pre deti do troch rokov.</p>

      <h2>Zodpovednosť</h2>
      <p>Kleurhoek vytvárame s veľkou starostlivosťou, ale nemôžeme sľúbiť, že všetko bude vždy bez chýb alebo že web bude vždy dostupný. V rozsahu, ktorý zákon dovoľuje, Kleurhoek nezodpovedá za škody vzniknuté používaním webu, obrázkov alebo webov, na ktoré odkazujeme.</p>

      <h2>Súkromie</h2>
      <p>Návštevy počítame anonymne: bez cookies, bez IP adries a bez čohokoľvek, čo by sa dalo vystopovať až k vám. Na vyfarbovanie ani tlač nepotrebujete účet. Ak si ho založíte, uchovávame vaše meno, e-mailovú adresu a obľúbené obrázky, aby ste ich mali na všetkých svojich zariadeniach; účet môžete kedykoľvek sami vymazať. Ak sa prihlásite na odber e-mailov, použijeme vašu adresu len na to a odhlásením ju vymažeme. Ak nám pošlete správu, použijeme vaše meno a e-mailovú adresu len na odpoveď a správu uchováme najviac dvanásť mesiacov. Chcete, aby sme vašu správu vymazali skôr? <Link href={contact("privacy")}>Dajte nám vedieť</Link>.</p>

      <h2>Zmeny a otázky</h2>
      <p>Toto upozornenie môžeme zmeniť, napríklad keď na Kleurhoek pribudne niečo nové. Dátum hore ukazuje, kedy bolo naposledy aktualizované. Toto upozornenie sa riadi holandským právom. Máte otázky? <Link href={contact()}>Ozvite sa nám</Link>.</p>
    </>
  );
}
