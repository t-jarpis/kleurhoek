import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Servisch, Latijns schrift (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Poslednje ažuriranje: 24. oktobar 2026.</p>
      <p>Na ovoj stranici objašnjavamo šta smeš da radiš sa bojankama i listovima za pravljenje sa Kleurhoeka, kako vodimo na druge sajtove i kako možeš nešto da nam prijaviš. Korišćenjem Kleurhoeka prihvataš ove uslove.</p>

      <h2>Naši sopstveni dizajni</h2>
      <p>Sve bojanke, listovi za isecanje i papirne makete na Kleurhoeku napravljeni su posebno za Kleurhoek. Pravimo ih uz pomoć veštačke inteligencije i proveravamo svaku stranicu pre nego što se pojavi na sajtu. Ništa ne kopiramo sa drugih sajtova ni iz knjiga i ne pravimo poznate likove, brendove ni figure. Sajt, ime Kleurhoek i kolekcija bojanki pripadaju Kleurhoeku.</p>
      <p>Bojanke smeš besplatno da koristiš:</p>
      <ul>
        <li>kod kuće, za bojenje, štampanje i deljenje porodici i prijateljima;</li>
        <li>u školi, vrtiću, klubu ili biblioteci, pa i u velikom broju primeraka;</li>
        <li>na proslavi, na primer kao kreativnu aktivnost.</li>
      </ul>
      <p>Bez naše pismene dozvole nije dozvoljeno: prodavati bojanke (pojedinačno, u knjižici ili kao preuzimanje), stavljati ih na drugi sajt, u aplikaciju ili na društvene mreže kao sopstveni materijal ili ih koristiti u proizvodima ili reklamama. Link do stranice na Kleurhoeku slobodno podeli.</p>

      <h2>Teme kod autora</h2>
      <p>Deca često traže bojanke sa likovima iz crtanog filma, zabavnog parka ili knjige. Ti crteži pripadaju svojim autorima i ne smemo sami da ih pravimo niti da ih kopiramo. Ali mnogi autori ih besplatno nude na svojim sajtovima. U odeljku <Link href={link(base, "/themas")}>Teme kod autora</Link> skupljamo linkove ka tim stranicama. Pri tome važi:</p>
      <ul>
        <li>Linkujemo samo na zvanični sajt autora ili nosioca prava, nikad na sajtove koji kopiraju tuđe crteže.</li>
        <li>Ne prikazujemo i ne čuvamo slike, crteže ni logotipe autora. Na našem sajtu vidiš samo naš opis i link. Drugačije može biti samo ako nam autor da pismenu dozvolu, i tada to navodimo.</li>
        <li>Svaki link proveravamo pre nego što se pojavi na sajtu. Posle toga računarski program svakog dana proverava da li stranica još postoji. Ako stranica nestane, link automatski uklanjamo. Pri tome uvek poštujemo pravila (robots.txt) sajta autora.</li>
        <li>Za sadržaj sajtova autora odgovorni su sami autori i za njega važe njihovi uslovi. Na njega nemamo uticaja.</li>
      </ul>
      <p>Ti si autor i želiš da promenimo ili uklonimo link, ili želiš da sarađuješ sa nama? <Link href={contact("partnership")}>Javi nam se</Link>. Promenu ćemo uraditi u roku od pet radnih dana.</p>

      <h2>Brendovi i imena</h2>
      <p>Imena likova, zabavnih parkova, serija i brendova pripadaju njihovim vlasnicima. Koristimo ih samo da opišemo gde nešto možeš da nađeš. Kleurhoek nije povezan sa tim vlasnicima niti ga oni sponzorišu, osim ako je to izričito navedeno.</p>

      <h2>Partnerski linkovi</h2>
      <p>Uz neke bojanke i teme navodimo stvari koje uz njih možeš da koristiš, na primer dečje makaze ili drvene bojice. To su partnerski linkovi: ako nešto kupiš preko takvog linka, Kleurhoek dobija malu naknadu od prodavnice. Ti plaćaš isto. Tako bojanke ostaju besplatne. Partnerski linkovi su uvek jasno označeni. Za proizvod, cenu i isporuku odgovorna je prodavnica.</p>

      <h2>Prijava kršenja autorskih prava</h2>
      <p>Misliš da se na Kleurhoeku nalazi nešto na šta ti imaš prava ili da neki link vodi tamo gde ne bi trebalo? Prijavi to preko <Link href={contact("copyright")}>kontakt formulara</Link> sa temom „Autorska prava”. Napiši o kojoj stranici se radi, zašto misliš da nešto nije u redu i kako možemo da te kontaktiramo. Odgovorićemo u roku od pet radnih dana i, ako ima razloga, ukloniti sadržaj dok to proveravamo.</p>

      <h2>Bezbedno pravljenje</h2>
      <p>Listovi za isecanje i papirne makete namenjeni su da se prave zajedno sa odraslom osobom. Koristi dečje makaze, a za lampione uvek LED svetlo, nikad pravu sveću. Sitni delovi nisu pogodni za decu mlađu od tri godine.</p>

      <h2>Odgovornost</h2>
      <p>Kleurhoek pravimo s velikom pažnjom, ali ne možemo da obećamo da je sve uvek bez grešaka niti da je sajt uvek dostupan. U meri u kojoj zakon to dozvoljava, Kleurhoek nije odgovoran za štetu nastalu korišćenjem sajta, bojanki ili sajtova na koje vodimo.</p>

      <h2>Privatnost</h2>
      <p>Posete brojimo anonimno: bez kolačića, bez IP adresa i bez ičega što bi moglo da se poveže sa tobom. Za bojenje ili štampanje nije ti potreban nalog. Ako ga ipak napraviš, čuvamo tvoje ime, imejl adresu i omiljene bojanke, da bi ih imao na svim uređajima; nalog možeš sam da obrišeš u bilo kom trenutku. Ako se prijaviš za imejlove, tvoju adresu koristimo samo za to, a odjavom se ona briše. Ako nam pošalješ poruku, tvoje ime i imejl adresu koristimo samo da ti odgovorimo, a poruku čuvamo najviše dvanaest meseci. Želiš da ranije obrišemo tvoju poruku? <Link href={contact("privacy")}>Javi nam</Link>.</p>

      <h2>Izmene i pitanja</h2>
      <p>Ove pravne napomene možemo da promenimo, na primer kada na Kleurhoeku dodamo nešto novo. Datum na vrhu pokazuje kada su poslednji put ažurirane. Na ove pravne napomene primenjuje se pravo Holandije. Imaš pitanja? <Link href={contact()}>Javi nam se</Link>.</p>
    </>
  );
}
