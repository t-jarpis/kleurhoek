import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Tsjechisch (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Naposledy aktualizováno 24. října 2026.</p>
      <p>Na této stránce se dozvíte, co smíte dělat s omalovánkami a vystřihovánkami Kleurhoek, jak odkazujeme na jiné weby a jak nám můžete něco nahlásit. Používáním Kleurhoeku s těmito podmínkami souhlasíte.</p>

      <h2>Naše vlastní návrhy</h2>
      <p>Všechny omalovánky, vystřihovánky a papírové modely na Kleurhoeku vznikly speciálně pro Kleurhoek. Vytváříme je s pomocí umělé inteligence a každý obrázek před zveřejněním kontrolujeme. Nic nekopírujeme z jiných webů ani z knih a nekreslíme známé postavičky, značky ani figurky. Web, název Kleurhoek a sbírka obrázků patří Kleurhoeku.</p>
      <p>Obrázky můžete používat zdarma:</p>
      <ul>
        <li>doma, k vybarvování, tisku a rozdávání rodině a přátelům;</li>
        <li>ve škole, ve školce, v kroužku nebo v knihovně, i ve velkém množství;</li>
        <li>na oslavě, například jako tvořivou aktivitu.</li>
      </ul>
      <p>Bez našeho písemného souhlasu není dovoleno: obrázky prodávat (jednotlivě, v sešitku ani ke stažení), zveřejňovat je na jiném webu, v aplikaci nebo na sociálních sítích jako vlastní materiál ani je používat ve výrobcích nebo v reklamě. Odkaz na stránku na Kleurhoeku sdílet můžete.</p>

      <h2>Témata od autorů</h2>
      <p>Děti často hledají omalovánky s postavičkami z pohádek, zábavních parků nebo knih. Tyto kresby patří jejich autorům a my je sami kreslit ani kopírovat nesmíme. Mnoho autorů je ale nabízí zdarma na svých vlastních webech. V části <Link href={link(base, "/themas")}>Témata od autorů</Link> sbíráme odkazy na tyto stránky. Platí přitom:</p>
      <ul>
        <li>Odkazujeme jen na oficiální web autora nebo držitele práv, nikdy na weby, které kopírují cizí kresby.</li>
        <li>Nezobrazujeme ani neukládáme žádné obrázky, kresby ani loga autora. Na našem webu vidíte jen náš vlastní popis a odkaz. Jinak tomu může být jen tehdy, když nám autor dá písemný souhlas; pak to uvádíme.</li>
        <li>Každý odkaz před zveřejněním kontrolujeme. Poté počítačový program každý den ověřuje, zda stránka stále existuje. Když stránka zmizí, odkaz automaticky odstraníme. Vždy přitom dodržujeme pravidla (robots.txt) webu autora.</li>
        <li>Za obsah webů autorů odpovídají sami autoři a platí pro něj jejich vlastní podmínky. Nemáme na něj žádný vliv.</li>
      </ul>
      <p>Jste autor a chcete, abychom odkaz upravili nebo odstranili, nebo s námi chcete spolupracovat? <Link href={contact("partnership")}>Ozvěte se nám</Link>. Změnu provedeme do pěti pracovních dnů.</p>

      <h2>Značky a názvy</h2>
      <p>Názvy postaviček, zábavních parků, seriálů a značek patří jejich vlastníkům. Používáme je jen k popisu, kde něco najdete. Kleurhoek není s těmito vlastníky spojen a není jimi sponzorován, pokud to není výslovně uvedeno.</p>

      <h2>Partnerské odkazy</h2>
      <p>U některých obrázků a témat zmiňujeme věci, které se k nim hodí, například dětské nůžky nebo pastelky. Jde o partnerské odkazy: když přes takový odkaz něco koupíte, dostane Kleurhoek od obchodu malou odměnu. Vy zaplatíte stejně. Díky tomu zůstávají obrázky zdarma. Partnerské odkazy jsou vždy jasně označené. Za výrobek, cenu a doručení odpovídá obchod.</p>

      <h2>Nahlášení porušení autorských práv</h2>
      <p>Myslíte si, že je na Kleurhoeku něco, k čemu máte práva vy, nebo že odkaz vede někam, kam by neměl? Nahlaste to přes <Link href={contact("copyright")}>kontaktní formulář</Link> s tématem &quot;Autorská práva&quot;. Uveďte, o kterou stránku jde, proč si myslíte, že to není v pořádku, a jak vás můžeme kontaktovat. Odpovíme do pěti pracovních dnů a pokud k tomu bude důvod, obsah po dobu prověřování odstraníme.</p>

      <h2>Bezpečné tvoření</h2>
      <p>Vystřihovánky a papírové modely jsou určeny k tvoření společně s dospělým. Používejte dětské nůžky a do lampionů vždy dávejte LED světlo, nikdy skutečnou svíčku. Malé díly nejsou vhodné pro děti do tří let.</p>

      <h2>Odpovědnost</h2>
      <p>Kleurhoek vytváříme s velkou péčí, ale nemůžeme slíbit, že vše bude vždy bez chyb nebo že web bude vždy dostupný. V rozsahu, který zákon dovoluje, neodpovídá Kleurhoek za škody vzniklé používáním webu, obrázků nebo webů, na které odkazujeme.</p>

      <h2>Soukromí</h2>
      <p>Návštěvy počítáme anonymně: bez cookies, bez IP adres a bez čehokoli, co by se dalo vysledovat až k vám. K vybarvování ani tisku nepotřebujete účet. Pokud si ho založíte, uchováváme vaše jméno, e-mailovou adresu a oblíbené obrázky, abyste je měli na všech svých zařízeních; účet můžete kdykoli sami smazat. Pokud se přihlásíte k odběru e-mailů, použijeme vaši adresu jen k tomu a odhlášením ji smažeme. Pokud nám pošlete zprávu, použijeme vaše jméno a e-mailovou adresu jen k odpovědi a zprávu uchováme nejvýše dvanáct měsíců. Chcete, abychom vaši zprávu smazali dříve? <Link href={contact("privacy")}>Dejte nám vědět</Link>.</p>

      <h2>Změny a otázky</h2>
      <p>Toto upozornění můžeme změnit, například když na Kleurhoek přibude něco nového. Datum nahoře ukazuje, kdy bylo naposledy aktualizováno. Toto upozornění se řídí nizozemským právem. Máte otázky? <Link href={contact()}>Ozvěte se nám</Link>.</p>
    </>
  );
}
