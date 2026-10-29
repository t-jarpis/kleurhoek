import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Sloveens (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Zadnja posodobitev: 24. oktober 2026.</p>
      <p>Na tej strani pojasnjujemo, kaj smeš početi s pobarvankami in predlogami za ustvarjanje s Kleurhoeka, kako povezujemo na druge spletne strani in kako nam lahko kaj sporočiš. Z uporabo Kleurhoeka se strinjaš s temi pogoji.</p>

      <h2>Naše lastne zasnove</h2>
      <p>Vse pobarvanke, predloge za izrezovanje in modeli iz papirja na Kleurhoeku so narejeni posebej za Kleurhoek. Ustvarjamo jih s pomočjo umetne inteligence in vsako stran preverimo, preden jo objavimo. Ničesar ne kopiramo z drugih spletnih strani ali iz knjig in ne poustvarjamo znanih likov, blagovnih znamk ali figur. Spletna stran, ime Kleurhoek in zbirka pobarvank pripadajo Kleurhoeku.</p>
      <p>Pobarvanke lahko brezplačno uporabljaš:</p>
      <ul>
        <li>doma, za barvanje, tiskanje in deljenje z družino in prijatelji;</li>
        <li>v šoli, vrtcu, društvu ali knjižnici, tudi v velikih količinah;</li>
        <li>na zabavi, na primer kot ustvarjalno dejavnost.</li>
      </ul>
      <p>Brez našega pisnega dovoljenja ni dovoljeno: prodajati pobarvanke (posamezno, v knjižici ali kot prenos), jih objavljati na drugi spletni strani, v aplikaciji ali na družbenih omrežjih kot lastno gradivo ali jih uporabljati v izdelkih ali oglaševanju. Povezavo do strani na Kleurhoeku pa lahko brez skrbi deliš.</p>

      <h2>Teme pri ustvarjalcih</h2>
      <p>Otroci pogosto iščejo pobarvanke z liki iz risank, zabaviščnih parkov ali knjig. Te risbe pripadajo njihovim ustvarjalcem, zato jih sami ne smemo izdelovati ali kopirati. Veliko ustvarjalcev pa jih brezplačno ponuja na svojih spletnih straneh. Pod <Link href={link(base, "/themas")}>Teme pri ustvarjalcih</Link> zbiramo povezave do teh strani. Pri tem velja:</p>
      <ul>
        <li>Povezujemo samo na uradno spletno stran ustvarjalca ali imetnika pravic, nikoli na strani, ki kopirajo tuje risbe.</li>
        <li>Ne prikazujemo in ne shranjujemo slik, risb ali logotipov ustvarjalca. Na naši strani vidiš samo naš opis in povezavo. Drugače je lahko le, če nam ustvarjalec da pisno dovoljenje, in takrat to navedemo.</li>
        <li>Vsako povezavo preverimo, preden jo objavimo. Nato računalniški program vsak dan preveri, ali stran še obstaja. Če stran izgine, povezavo samodejno odstranimo. Pri tem vedno upoštevamo pravila (robots.txt) spletne strani ustvarjalca.</li>
        <li>Za vsebino spletnih strani ustvarjalcev so odgovorni ustvarjalci sami in zanjo veljajo njihovi pogoji. Nanjo nimamo vpliva.</li>
      </ul>
      <p>Si ustvarjalec in želiš, da povezavo spremenimo ali odstranimo, ali bi rad sodeloval z nami? <Link href={contact("partnership")}>Piši nam</Link>. Spremembo bomo uredili v petih delovnih dneh.</p>

      <h2>Blagovne znamke in imena</h2>
      <p>Imena likov, zabaviščnih parkov, serij in blagovnih znamk pripadajo njihovim lastnikom. Uporabljamo jih samo zato, da opišemo, kje je kaj mogoče najti. Kleurhoek ni povezan s temi lastniki in ga ne sponzorirajo, razen če je to izrecno navedeno.</p>

      <h2>Partnerske povezave</h2>
      <p>Pri nekaterih pobarvankah in temah navedemo stvari, ki ti lahko pridejo prav, na primer otroške škarje ali barvice. To so partnerske povezave: če prek takšne povezave kaj kupiš, Kleurhoek od trgovine dobi majhno nadomestilo. Ti plačaš enako. Tako pobarvanke ostajajo brezplačne. Partnerske povezave so vedno jasno označene. Za izdelek, ceno in dostavo je odgovorna trgovina.</p>

      <h2>Prijava kršitve avtorskih pravic</h2>
      <p>Misliš, da je na Kleurhoeku kaj, do česar imaš pravice, ali da povezava vodi tja, kamor ne bi smela? Sporoči nam prek <Link href={contact("copyright")}>kontaktnega obrazca</Link> z zadevo &quot;Avtorske pravice&quot;. Navedi, za katero stran gre, zakaj misliš, da ni v redu, in kako te lahko dosežemo. Odgovorili bomo v petih delovnih dneh in, če je za to razlog, vsebino odstranili, dokler zadevo preverjamo.</p>

      <h2>Varno ustvarjanje</h2>
      <p>Predloge za izrezovanje in modeli iz papirja so namenjeni temu, da jih izdelaš skupaj z odraslo osebo. Uporabljaj otroške škarje, za lampijone pa vedno lučko LED in nikoli prave sveče. Majhni deli niso primerni za otroke, mlajše od treh let.</p>

      <h2>Odgovornost</h2>
      <p>Kleurhoek ustvarjamo z veliko skrbnostjo, vendar ne moremo obljubiti, da je vse vedno brez napak ali da je spletna stran vedno dosegljiva. V obsegu, ki ga dovoljuje zakon, Kleurhoek ne odgovarja za škodo, ki nastane zaradi uporabe spletne strani, pobarvank ali spletnih strani, na katere povezujemo.</p>

      <h2>Zasebnost</h2>
      <p>Obiske štejemo anonimno: brez piškotkov, brez naslovov IP in brez česar koli, kar bi se dalo povezati s tabo. Za barvanje ali tiskanje ne potrebuješ računa. Če ga vseeno ustvariš, hranimo tvoje ime, e-poštni naslov in priljubljene, da jih imaš na vseh svojih napravah; račun lahko kadar koli sam izbrišeš. Če se prijaviš na naša e-poštna sporočila, tvoj naslov uporabimo samo za to, z odjavo pa ga izbrišemo. Če nam pošlješ sporočilo, tvoje ime in e-poštni naslov uporabimo samo za odgovor, sporočilo pa hranimo največ dvanajst mesecev. Želiš, da tvoje sporočilo izbrišemo prej? <Link href={contact("privacy")}>Sporoči nam</Link>.</p>

      <h2>Spremembe in vprašanja</h2>
      <p>To pravno obvestilo lahko spremenimo, na primer ko na Kleurhoek dodamo kaj novega. Datum na vrhu kaže, kdaj je bilo nazadnje posodobljeno. Za to pravno obvestilo velja nizozemsko pravo. Imaš vprašanje? <Link href={contact()}>Piši nam</Link>.</p>
    </>
  );
}
