import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Kroatisch (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Posljednje ažuriranje: 24. listopada 2026.</p>
      <p>Na ovoj stranici objašnjavamo što smiješ raditi s bojankama i predlošcima za izradu s Kleurhoeka, kako vodimo na druge web-stranice i kako nam nešto možeš prijaviti. Korištenjem Kleurhoeka prihvaćaš ove uvjete.</p>

      <h2>Naši vlastiti dizajni</h2>
      <p>Sve bojanke, predlošci za izrezivanje i papirnati modeli na Kleurhoeku napravljeni su posebno za Kleurhoek. Izrađujemo ih uz pomoć umjetne inteligencije i svaku stranicu provjerimo prije objave. Ništa ne kopiramo s drugih web-stranica ni iz knjiga i ne izrađujemo poznate likove, marke ni figure. Web-stranica, ime Kleurhoek i zbirka bojanki pripadaju Kleurhoeku.</p>
      <p>Bojanke smiješ besplatno koristiti:</p>
      <ul>
        <li>kod kuće, za bojanje, ispis i dijeljenje obitelji i prijateljima;</li>
        <li>u školi, vrtiću, klubu ili knjižnici, i u velikim količinama;</li>
        <li>na zabavi, na primjer kao kreativnu aktivnost.</li>
      </ul>
      <p>Bez našeg pisanog dopuštenja nije dopušteno: prodavati bojanke (pojedinačno, u knjižici ili kao preuzimanje), objavljivati ih na drugoj web-stranici, u aplikaciji ili na društvenim mrežama kao vlastiti materijal te ih koristiti u proizvodima ili oglašavanju. Link na stranicu na Kleurhoeku slobodno podijeli.</p>

      <h2>Teme kod autora</h2>
      <p>Djeca često traže bojanke s likovima iz crtića, zabavnog parka ili knjige. Ti crteži pripadaju svojim autorima i ne smijemo ih sami izrađivati ni kopirati. No mnogi ih autori besplatno nude na svojim web-stranicama. Pod <Link href={link(base, "/themas")}>Teme kod autora</Link> skupljamo linkove na te stranice. Pritom vrijedi:</p>
      <ul>
        <li>Vodimo samo na službenu web-stranicu autora ili nositelja prava, nikad na stranice koje kopiraju tuđe crteže.</li>
        <li>Ne prikazujemo i ne pohranjujemo slike, crteže ni logotipe autora. Na našoj stranici vidiš samo naš opis i link. Iznimka je moguća samo ako nam autor da pisano dopuštenje, i tada to navodimo.</li>
        <li>Svaki link provjerimo prije objave. Nakon toga računalni program svaki dan provjerava postoji li stranica još. Ako stranica nestane, link automatski uklanjamo. Pritom uvijek poštujemo pravila (robots.txt) web-stranice autora.</li>
        <li>Za sadržaj web-stranica autora odgovorni su sami autori i na njega se primjenjuju njihovi uvjeti. Na njega nemamo utjecaja.</li>
      </ul>
      <p>Jesi li autor i želiš li da promijenimo ili uklonimo link, ili bi htio surađivati s nama? <Link href={contact("partnership")}>Javi nam se</Link>. Promjenu ćemo napraviti u roku od pet radnih dana.</p>

      <h2>Marke i imena</h2>
      <p>Imena likova, zabavnih parkova, serija i marki pripadaju njihovim vlasnicima. Koristimo ih samo da opišemo gdje se nešto može pronaći. Kleurhoek nije povezan s tim vlasnicima niti ga oni sponzoriraju, osim ako je to izričito navedeno.</p>

      <h2>Partnerski linkovi</h2>
      <p>Uz neke bojanke i teme navodimo stvari koje ti mogu poslužiti, poput dječjih škarica ili drvenih bojica. To su partnerski linkovi: ako preko takvog linka nešto kupiš, Kleurhoek od trgovine dobiva malu naknadu. Ti plaćaš isto. Tako bojanke ostaju besplatne. Partnerski linkovi uvijek su jasno označeni. Za proizvod, cijenu i dostavu odgovorna je trgovina.</p>

      <h2>Prijava kršenja autorskih prava</h2>
      <p>Misliš li da se na Kleurhoeku nalazi nešto na što imaš prava ili da neki link vodi na nešto na što ne bi smio? Prijavi to putem <Link href={contact("copyright")}>kontaktnog obrasca</Link> s temom &quot;Autorska prava&quot;. Napiši o kojoj se stranici radi, zašto misliš da nešto nije u redu i kako te možemo kontaktirati. Odgovorit ćemo u roku od pet radnih dana i, ako za to postoji razlog, sadržaj ukloniti dok stvar provjeravamo.</p>

      <h2>Sigurna izrada</h2>
      <p>Predlošci za izrezivanje i papirnati modeli namijenjeni su izradi zajedno s odraslom osobom. Koristi dječje škarice, a za lampione uvijek LED svjetlo, nikad pravu svijeću. Sitni dijelovi nisu prikladni za djecu mlađu od tri godine.</p>

      <h2>Odgovornost</h2>
      <p>Kleurhoek izrađujemo s velikom pažnjom, ali ne možemo obećati da je sve uvijek bez pogrešaka ni da je web-stranica uvijek dostupna. U mjeri u kojoj to zakon dopušta, Kleurhoek ne odgovara za štetu nastalu korištenjem web-stranice, bojanki ili web-stranica na koje vodimo.</p>

      <h2>Privatnost</h2>
      <p>Posjete brojimo anonimno: bez kolačića, bez IP adresa i bez ičega što bi se moglo povezati s tobom. Za bojanje ili ispis ne trebaš račun. Ako ga ipak otvoriš, čuvamo tvoje ime, adresu e-pošte i favorite kako bi ih imao na svim uređajima; račun možeš sam izbrisati u bilo kojem trenutku. Ako se prijaviš na naše poruke e-poštom, tvoju adresu koristimo samo za to, a odjavom se ona briše. Ako nam pošalješ poruku, tvoje ime i adresu e-pošte koristimo samo da ti odgovorimo, a poruku čuvamo najviše dvanaest mjeseci. Želiš li da tvoju poruku izbrišemo ranije? <Link href={contact("privacy")}>Javi nam</Link>.</p>

      <h2>Promjene i pitanja</h2>
      <p>Ove pravne napomene možemo promijeniti, na primjer kad na Kleurhoek dodamo nešto novo. Datum na vrhu pokazuje kada su posljednji put ažurirane. Na ove pravne napomene primjenjuje se nizozemsko pravo. Imaš pitanje? <Link href={contact()}>Javi nam se</Link>.</p>
    </>
  );
}
