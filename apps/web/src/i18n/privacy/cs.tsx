import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Naposledy aktualizováno 4. listopadu 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be a www.kleurhoek.com) je web s vlastními omalovánkami a tvořivými listy pro děti. Shromažďujeme co nejméně. Na této stránce přesně popisujeme, co přesto uchováváme, proč, jak dlouho a jaká máš práva.</p>

      <h2>Kdo jsme</h2>
      <p>Kleurhoek je nizozemský web. S dotazy k ochraně soukromí použij náš <Link href={contact("privacy")}>kontaktní formulář</Link>.</p>

      <h2>Návštěvy a vybarvování</h2>
      <p>Návštěvy počítáme anonymně: bez cookies, bez IP adres a bez čehokoli, co by se dalo vysledovat zpět k tobě. Nepoužíváme reklamní ani sledovací skripty nikoho jiného, ani od Google, Meta nebo Pinterest. Vybarvovat, tisknout i vybarvovat společně můžeš bez účtu. Co vybarvíš, zůstane v tvém zařízení. Když vybarvuješ společně s ostatními, tahy putují přes náš server k ostatním v místnosti, bez jakýchkoli jmen; když se 30 minut nevybarvuje, místnost se ukončí. Jména, která napíšeš na dárkové štítky, se nikdy neposílají na náš server.</p>
      <p>Abychom návštěvníky nepočítali dvakrát, vytváříme každý den kód z tvé IP adresy a prohlížeče pomocí klíče, který se každý den mění; samotnou IP adresu neukládáme. Po 90 dnech tento kód nahradíme náhodným, takže už ani my nedokážeme přiřadit záznam k zařízení. Samotné počty (která stránka, která země, telefon nebo počítač, kdy) uchováváme, abychom viděli, jak se web v průběhu let používá.</p>

      <h2>Účet</h2>
      <p>Účty jsou jen pro dospělé (od 16 let). Děti účet nepotřebují a nemohou si ho založit. Pokud máš účet, uchováváme tvoje jméno, e-mailovou adresu a oblíbené, aby byly dostupné na všech tvých zařízeních. Účet si můžeš smazat samostatně; spolu s ním se smažou i tvoje oblíbené a přihlášení k odběru e-mailů.</p>

      <h2>E-maily</h2>
      <p>Pokud se přihlásíš k odběru e-mailů, uchováváme tvoji e-mailovou adresu, zvolená témata a tvoji zemi a jazyk. Přihlášení nejdřív potvrdíš přes odkaz. Naše e-maily neobsahují sledovací pixely ani přesměrované odkazy, které by měřily, zda je otevíráš. Odhlásit se můžeš jedním kliknutím dole v každém e-mailu a tvoji adresu pak smažeme.</p>

      <h2>Kontakt</h2>
      <p>Pokud nám pošleš zprávu, tvoje jméno a e-mailovou adresu použijeme jen k odpovědi. Zprávu uchováváme nejvýše dvanáct měsíců.</p>

      <h2>Pinterest, Facebook a Instagram</h2>
      <p>Kleurhoek zveřejňuje vlastní omalovánky na vlastních účtech Kleurhoek na Pinterestu, Facebooku a Instagramu. K tomu tyto účty propojujeme přes oficiální přihlášení (OAuth) služeb Pinterest a Meta. Přístupové tokeny tohoto propojení ukládáme zašifrované a používáme je jen ke zveřejňování příspěvků a vytváření nástěnek na našich vlastních účtech. Nečteme, neshromažďujeme ani neukládáme údaje o jiných uživatelích těchto služeb a propojení nepoužíváme k reklamě. Tlačítko „Uložit na Pinterest“ na našem webu je obyčejný odkaz: nenačítá se žádný skript od Pinterestu. Propojení lze kdykoli zrušit a tokeny pak smažeme.</p>

      <h2>Kdo nám pomáhá</h2>
      <p>Web běží u Scaleway v Amsterdamu. Cloudflare zajišťuje rychlost a zabezpečení, Zitadel přihlašování a Brevo rozesílá naše e-maily. Zpracovávají údaje jen naším jménem a jen k tomuto účelu. Když klikneš na odkaz do obchodu, například Amazon, platí od té chvíle zásady ochrany soukromí daného obchodu.</p>

      <h2>Tvoje práva</h2>
      <p>Můžeš se zeptat, jaké údaje o tobě máme, a nechat je opravit nebo smazat. Stačí se nám <Link href={contact("privacy")}>ozvat</Link>. Pokud nesouhlasíš s tím, jak s tvými údaji zacházíme, můžeš podat stížnost u Autoriteit Persoonsgegevens (nizozemského úřadu pro ochranu osobních údajů) nebo u úřadu ve své zemi.</p>

      <h2>Změny</h2>
      <p>Pokud se změní něco v tom, co uchováváme, tuto stránku aktualizujeme. Datum nahoře ukazuje, kdy byla naposledy aktualizována.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Zásady ochrany soukromí", description: "Jaké údaje Kleurhoek uchovává, proč a jak dlouho: žádné cookies, anonymní počítání návštěv a účty jen pro dospělé.", Body };
