import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Naposledy aktualizované 4. novembra 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be a www.kleurhoek.com) je web s vlastnými omaľovánkami a tvorivými listami pre deti. Zbierame čo najmenej. Na tejto stránke presne opisujeme, čo predsa uchovávame, prečo, ako dlho a aké máš práva.</p>

      <h2>Kto sme</h2>
      <p>Kleurhoek je holandský web. S otázkami o ochrane súkromia použi náš <Link href={contact("privacy")}>kontaktný formulár</Link>.</p>

      <h2>Návštevy a vyfarbovanie</h2>
      <p>Návštevy počítame anonymne: bez cookies, bez IP adries a bez čohokoľvek, čo by sa dalo spätne priradiť k tebe. Nepoužívame reklamné ani sledovacie skripty nikoho iného, ani od Google, Meta či Pinterest. Vyfarbovať, tlačiť aj vyfarbovať spoločne môžeš bez účtu. Čo vyfarbíš, zostane v tvojom zariadení. Keď vyfarbuješ spoločne s ostatnými, ťahy idú cez náš server k ostatným v miestnosti, bez akýchkoľvek mien; keď sa 30 minút nevyfarbuje, miestnosť sa ukončí. Mená, ktoré napíšeš na darčekové štítky, sa nikdy neposielajú na náš server.</p>
      <p>Aby sme návštevníkov nepočítali dvakrát, vytvárame každý deň kód z tvojej IP adresy a prehliadača pomocou kľúča, ktorý sa každý deň mení; samotnú IP adresu neukladáme. Po 90 dňoch tento kód nahradíme náhodným, takže už ani my nedokážeme priradiť záznam k zariadeniu. Samotné počty (ktorá stránka, ktorá krajina, telefón alebo počítač, kedy) uchovávame, aby sme videli, ako sa web v priebehu rokov používa.</p>

      <h2>Účet</h2>
      <p>Účty sú len pre dospelých (od 16 rokov). Deti účet nepotrebujú a nemôžu si ho založiť. Ak máš účet, uchovávame tvoje meno, e-mailovú adresu a obľúbené, aby boli dostupné na všetkých tvojich zariadeniach. Účet si môžeš zmazať samostatne; spolu s ním sa zmažú aj tvoje obľúbené a prihlásenie na odber e-mailov.</p>

      <h2>E-maily</h2>
      <p>Ak sa prihlásiš na odber e-mailov, uchovávame tvoju e-mailovú adresu, zvolené témy a tvoju krajinu a jazyk. Prihlásenie najprv potvrdíš cez odkaz. Naše e-maily neobsahujú sledovacie pixely ani presmerované odkazy, ktoré by merali, či ich otváraš. Odhlásiť sa môžeš jedným kliknutím na konci každého e-mailu a tvoju adresu potom zmažeme.</p>

      <h2>Kontakt</h2>
      <p>Ak nám pošleš správu, tvoje meno a e-mailovú adresu použijeme len na odpoveď. Správu uchovávame najviac dvanásť mesiacov.</p>

      <h2>Pinterest, Facebook a Instagram</h2>
      <p>Kleurhoek zverejňuje vlastné omaľovánky na vlastných účtoch Kleurhoek na Pintereste, Facebooku a Instagrame. Na to tieto účty prepájame cez oficiálne prihlásenie (OAuth) služieb Pinterest a Meta. Prístupové tokeny tohto prepojenia ukladáme zašifrované a používame ich len na zverejňovanie príspevkov a vytváranie nástenok na našich vlastných účtoch. Nečítame, nezbierame ani neukladáme údaje o iných používateľoch týchto služieb a prepojenie nepoužívame na reklamu. Tlačidlo „Uložiť na Pinterest“ na našom webe je obyčajný odkaz: nenačítava sa žiadny skript od Pinterestu. Prepojenie sa dá kedykoľvek zrušiť a tokeny potom zmažeme.</p>

      <h2>Kto nám pomáha</h2>
      <p>Web beží u Scaleway v Amsterdame. Cloudflare zabezpečuje rýchlosť a bezpečnosť, Zitadel prihlasovanie a Brevo rozosiela naše e-maily. Spracúvajú údaje len v našom mene a len na tento účel. Keď klikneš na odkaz do obchodu, napríklad Amazon, od tej chvíle platia zásady ochrany súkromia daného obchodu.</p>

      <h2>Tvoje práva</h2>
      <p>Môžeš sa opýtať, aké údaje o tebe máme, a dať ich opraviť alebo vymazať. Stačí sa nám <Link href={contact("privacy")}>ozvať</Link>. Ak nesúhlasíš s tým, ako s tvojimi údajmi zaobchádzame, môžeš podať sťažnosť na Autoriteit Persoonsgegevens (holandský úrad na ochranu osobných údajov) alebo na úrad vo svojej krajine.</p>

      <h2>Zmeny</h2>
      <p>Ak sa zmení niečo v tom, čo uchovávame, túto stránku aktualizujeme. Dátum hore ukazuje, kedy bola naposledy aktualizovaná.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Zásady ochrany súkromia", description: "Aké údaje Kleurhoek uchováva, prečo a ako dlho: žiadne cookies, anonymné počítanie návštev a účty len pre dospelých.", Body };
