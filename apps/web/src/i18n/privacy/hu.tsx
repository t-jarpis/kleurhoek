import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Utolsó frissítés: 2026. november 4.</p>
      <p>A Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be és www.kleurhoek.com) saját színezőket és kézműves lapokat kínáló weboldal gyerekeknek. A lehető legkevesebb adatot gyűjtjük. Ezen az oldalon pontosan leírjuk, mit tárolunk mégis, miért, mennyi ideig, és milyen jogaid vannak.</p>

      <h2>Kik vagyunk</h2>
      <p>A Kleurhoek holland weboldal. Adatvédelmi kérdésekkel a <Link href={contact("privacy")}>kapcsolatfelvételi űrlapon</Link> fordulj hozzánk.</p>

      <h2>Látogatás és színezés</h2>
      <p>A látogatásokat névtelenül számoljuk: sütik nélkül, IP-címek nélkül, és semmi olyan nélkül, ami visszavezethető lenne hozzád. Nem használunk mások hirdetési vagy követő szkriptjeit, így a Google, a Meta vagy a Pinterest szkriptjeit sem. Színezni, nyomtatni és közösen színezni fiók nélkül is lehet. Amit kiszínezel, a saját eszközödön marad. Ha közösen színezel, a vonások a szerverünkön keresztül jutnak el a szoba többi résztvevőjéhez, nevek nélkül; ha 30 percig senki sem színez, a szoba bezárul. Az ajándékcímkékre beírt nevek soha nem kerülnek a szerverünkre.</p>
      <p>Hogy egy látogatót ne számoljunk kétszer, naponta kódot képezünk az IP-címedből és a böngésződből egy naponta változó kulccsal; magát az IP-címet nem tároljuk. 90 nap után ezt a kódot egy véletlenszerűre cseréljük, így már mi sem tudunk egy számlálást eszközhöz kötni. Magukat a számlálásokat (melyik oldal, melyik ország, telefon vagy számítógép, mikor) megőrizzük, hogy lássuk, hogyan használják az oldalt az évek során.</p>

      <h2>Fiók</h2>
      <p>Fiók csak felnőtteknek van (16 éves kortól). A gyerekeknek nincs szükségük fiókra, és nem is hozhatnak létre. Ha van fiókod, tároljuk a nevedet, az e-mail-címedet és a kedvenceidet, hogy minden eszközödön megtaláld őket. A fiókodat magad is törölheted; vele együtt törlődnek a kedvenceid és az e-mail-feliratkozásod is.</p>

      <h2>E-mail</h2>
      <p>Ha feliratkozol e-mailekre, tároljuk az e-mail-címedet, a választott témákat, valamint az országodat és a nyelvedet. A feliratkozást először egy linken keresztül megerősíted. E-mailjeinkben nincsenek követőpixelek vagy átirányított linkek, amelyekkel mérnénk, hogy megnyitod-e őket. Minden e-mail alján egy kattintással leiratkozhatsz, ekkor töröljük a címedet.</p>

      <h2>Kapcsolat</h2>
      <p>Ha üzenetet küldesz nekünk, a nevedet és az e-mail-címedet csak a válaszhoz használjuk. Az üzenetet legfeljebb tizenkét hónapig őrizzük meg.</p>

      <h2>Pinterest, Facebook és Instagram</h2>
      <p>A Kleurhoek saját színezőit a Kleurhoek saját Pinterest-, Facebook- és Instagram-fiókjain teszi közzé. Ehhez ezeket a fiókokat a Pinterest és a Meta hivatalos bejelentkezésén (OAuth) keresztül kapcsoljuk össze. A kapcsolathoz tartozó hozzáférési tokeneket titkosítva tároljuk, és csak arra használjuk, hogy bejegyzéseket tegyünk közzé és táblákat hozzunk létre a saját fiókjainkon. Nem olvasunk, nem gyűjtünk és nem tárolunk adatokat e szolgáltatások más felhasználóiról, és a kapcsolatot nem használjuk hirdetésekhez. Az oldalunkon lévő „Mentés a Pinterestre” gomb egyszerű link: nem töltődik be Pinterest-szkript. A kapcsolat bármikor megszüntethető, ezután töröljük a tokeneket.</p>

      <h2>Kik segítenek nekünk</h2>
      <p>A weboldal a Scaleway szerverein fut Amszterdamban. A Cloudflare a gyorsaságról és a biztonságról gondoskodik, a Zitadel a bejelentkezésről, a Brevo pedig az e-mailjeink kiküldéséről. Ők csak a megbízásunkból és csak erre a célra kezelnek adatokat. Ha egy bolt, például az Amazon linkjére kattintasz, attól kezdve az adott bolt adatvédelmi szabályai érvényesek.</p>

      <h2>Jogaid</h2>
      <p>Megkérdezheted, milyen adatokat tárolunk rólad, és kérheted ezek helyesbítését vagy törlését. Ehhez <Link href={contact("privacy")}>vedd fel velünk a kapcsolatot</Link>. Ha nem értesz egyet azzal, ahogyan az adataidat kezeljük, panaszt tehetsz az Autoriteit Persoonsgegevens (a holland adatvédelmi hatóság) vagy a saját országod hatósága felé.</p>

      <h2>Változások</h2>
      <p>Ha bármi változik abban, amit tárolunk, frissítjük ezt az oldalt. A fenti dátum mutatja, mikor frissült utoljára.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Adatvédelmi tájékoztató", description: "Milyen adatokat tárol a Kleurhoek, miért és mennyi ideig: nincsenek sütik, névtelen látogatásszámlálás, fiók csak felnőtteknek.", Body };
