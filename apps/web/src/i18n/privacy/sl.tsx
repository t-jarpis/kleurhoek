import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Zadnja posodobitev: 4. novembra 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be in www.kleurhoek.com) je spletna stran z lastnimi pobarvankami in ustvarjalnimi listi za otroke. Zbiramo čim manj. Na tej strani natančno opisujemo, kaj vseeno hranimo, zakaj, kako dolgo in kakšne so tvoje pravice.</p>

      <h2>Kdo smo</h2>
      <p>Kleurhoek je nizozemska spletna stran. Za vprašanja o zasebnosti uporabi naš <Link href={contact("privacy")}>kontaktni obrazec</Link>.</p>

      <h2>Obiski in barvanje</h2>
      <p>Obiske štejemo anonimno: brez piškotkov, brez naslovov IP in brez česar koli, kar bi se dalo povezati s tabo. Ne uporabljamo oglaševalskih skript ali skript za sledenje drugih, tudi ne podjetij Google, Meta ali Pinterest. Barvaš, tiskaš in barvaš skupaj lahko brez računa. Kar pobarvaš, ostane na tvoji napravi. Ko barvaš skupaj z drugimi, potezi potujejo prek našega strežnika do ostalih v sobi, brez imen; po 30 minutah brez barvanja se soba ustavi. Imena, ki jih vpišeš za darilne nalepke, se nikoli ne pošljejo na naš strežnik.</p>
      <p>Da obiskovalcev ne bi šteli dvakrat, vsak dan iz tvojega naslova IP in brskalnika naredimo kodo s ključem, ki se vsak dan spremeni; samega naslova IP ne shranjujemo. Po 90 dneh to kodo zamenjamo z naključno, tako da tudi mi štetja ne moremo več povezati z napravo. Sama štetja (katera stran, katera država, telefon ali računalnik, kdaj) hranimo, da vidimo, kako se stran uporablja skozi leta.</p>

      <h2>Račun</h2>
      <p>Računi so samo za odrasle (od 16 let). Otroci računa ne potrebujejo in ga ne morejo ustvariti. Če imaš račun, hranimo tvoje ime, e-poštni naslov in priljubljene, da so ti na voljo na vseh tvojih napravah. Račun lahko izbrišeš samostojno; skupaj z njim se izbrišejo tudi tvoje priljubljene in prijava na e-pošto.</p>

      <h2>E-pošta</h2>
      <p>Če se prijaviš na e-pošto, hranimo tvoj e-poštni naslov, teme, ki jih izbereš, ter tvojo državo in jezik. Prijavo najprej potrdiš prek povezave. Naša sporočila ne vsebujejo slikovnih pik za sledenje ali preusmerjenih povezav, s katerimi bi merili, ali jih odpreš. Odjaviš se lahko z enim klikom na dnu vsakega sporočila, nato pa tvoj naslov izbrišemo.</p>

      <h2>Kontakt</h2>
      <p>Če nam pošlješ sporočilo, tvoje ime in e-poštni naslov uporabimo samo za odgovor. Sporočilo hranimo največ dvanajst mesecev.</p>

      <h2>Pinterest, Facebook in Instagram</h2>
      <p>Kleurhoek objavlja lastne pobarvanke na lastnih računih Kleurhoek na Pinterestu, Facebooku in Instagramu. Za to te račune povežemo prek uradne prijave (OAuth) storitev Pinterest in Meta. Dostopne žetone za to povezavo hranimo šifrirane in jih uporabljamo samo za objavljanje objav in ustvarjanje tabel na naših lastnih računih. Ne beremo, ne zbiramo in ne hranimo podatkov o drugih uporabnikih teh storitev, povezave pa ne uporabljamo za oglaševanje. Gumb »Shrani na Pinterest« na naši strani je navadna povezava: ne naloži se nobena skripta Pinteresta. Povezavo je mogoče kadar koli odstraniti, nato pa žetone izbrišemo.</p>

      <h2>Kdo nam pomaga</h2>
      <p>Spletna stran teče pri podjetju Scaleway v Amsterdamu. Cloudflare skrbi za hitrost in varnost, Zitadel za prijavo, Brevo pa pošilja našo e-pošto. Podatke obdelujejo samo v našem imenu in samo za ta namen. Če klikneš povezavo do trgovine, na primer Amazon, od takrat velja pravilnik o zasebnosti te trgovine.</p>

      <h2>Tvoje pravice</h2>
      <p>Lahko vprašaš, katere podatke imamo o tebi, ter zahtevaš, da jih popravimo ali izbrišemo. Za to se nam <Link href={contact("privacy")}>oglasi</Link>. Če se ne strinjaš s tem, kako ravnamo s tvojimi podatki, lahko vložiš pritožbo pri Autoriteit Persoonsgegevens (nizozemskem organu za varstvo podatkov) ali pri organu v svoji državi.</p>

      <h2>Spremembe</h2>
      <p>Če se kaj spremeni pri tem, kar hranimo, bomo to stran posodobili. Datum na vrhu kaže, kdaj je bila nazadnje posodobljena.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Pravilnik o zasebnosti", description: "Katere podatke hrani Kleurhoek, zakaj in kako dolgo: brez piškotkov, anonimno štetje obiskov in računi samo za odrasle.", Body };
