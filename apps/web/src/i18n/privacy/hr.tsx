import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Posljednje ažuriranje: 4. studenoga 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be i www.kleurhoek.com) internetska je stranica s vlastitim bojankama i listovima za kreativne radove za djecu. Prikupljamo što je manje moguće. Na ovoj stranici točno navodimo što ipak čuvamo, zašto, koliko dugo i koja su tvoja prava.</p>

      <h2>Tko smo</h2>
      <p>Kleurhoek je nizozemska internetska stranica. Za pitanja o privatnosti upotrijebi naš <Link href={contact("privacy")}>obrazac za kontakt</Link>.</p>

      <h2>Posjeti i bojanje</h2>
      <p>Posjete brojimo anonimno: bez kolačića, bez IP adresa i bez ičega što bi se moglo povezati s tobom. Ne koristimo oglasne skripte ni skripte za praćenje drugih, pa ni skripte tvrtki Google, Meta ili Pinterest. Bojati, ispisivati i bojati zajedno možeš bez računa. Ono što obojiš ostaje na tvom uređaju. Kad bojaš zajedno s drugima, potezi idu preko našeg poslužitelja do ostalih u sobi, bez imena; nakon 30 minuta bez bojanja soba se zatvara. Imena koja upišeš za naljepnice za poklone nikad se ne šalju na naš poslužitelj.</p>
      <p>Kako posjetitelje ne bismo brojali dvaput, svaki dan iz tvoje IP adrese i preglednika izrađujemo kod pomoću ključa koji se mijenja svaki dan; samu IP adresu ne spremamo. Nakon 90 dana taj kod zamjenjujemo nasumičnim, tako da ni mi više ne možemo povezati brojanje s uređajem. Sama brojanja (koja stranica, koja zemlja, mobitel ili računalo, kada) čuvamo kako bismo vidjeli kako se stranica koristi tijekom godina.</p>

      <h2>Račun</h2>
      <p>Računi su samo za odrasle (od 16 godina). Djeci ne treba račun i ne mogu ga otvoriti. Ako imaš račun, čuvamo tvoje ime, adresu e-pošte i favorite kako bi ti bili dostupni na svim tvojim uređajima. Račun možeš izbrisati samostalno; s njim se brišu i tvoji favoriti i prijava na e-poštu.</p>

      <h2>E-pošta</h2>
      <p>Ako se prijaviš za primanje e-pošte, čuvamo tvoju adresu e-pošte, teme koje odabereš te tvoju zemlju i jezik. Prijavu najprije potvrđuješ putem poveznice. Naše poruke ne sadrže piksele za praćenje ni preusmjerene poveznice kojima bi se mjerilo otvaraš li ih. Odjaviti se možeš jednim klikom na dnu svake poruke, a tada brišemo tvoju adresu.</p>

      <h2>Kontakt</h2>
      <p>Ako nam pošalješ poruku, tvoje ime i adresu e-pošte koristimo samo da ti odgovorimo. Poruku čuvamo najdulje dvanaest mjeseci.</p>

      <h2>Pinterest, Facebook i Instagram</h2>
      <p>Kleurhoek objavljuje vlastite bojanke na vlastitim Kleurhoek računima na Pinterestu, Facebooku i Instagramu. U tu svrhu povezujemo te račune putem službene prijave (OAuth) servisa Pinterest i Meta. Pristupne tokene te veze čuvamo šifrirane i koristimo ih samo za objavljivanje objava i izradu ploča na našim vlastitim računima. Ne čitamo, ne prikupljamo i ne čuvamo podatke o drugim korisnicima tih usluga i ne koristimo vezu za oglašavanje. Gumb „Spremi na Pinterest” na našoj stranici obična je poveznica: ne učitava se nikakva skripta Pinteresta. Veza se može ukloniti u bilo kojem trenutku, nakon čega brišemo tokene.</p>

      <h2>Tko nam pomaže</h2>
      <p>Stranica radi na poslužiteljima tvrtke Scaleway u Amsterdamu. Cloudflare brine za brzinu i sigurnost, Zitadel za prijavu, a Brevo šalje našu e-poštu. Oni obrađuju podatke samo u naše ime i samo u tu svrhu. Ako klikneš na poveznicu prema trgovini kao što je Amazon, od tog trenutka vrijede pravila privatnosti te trgovine.</p>

      <h2>Tvoja prava</h2>
      <p>Možeš pitati koje podatke o tebi imamo te zatražiti da se isprave ili izbrišu. Za to nam se <Link href={contact("privacy")}>javi</Link>. Ako se ne slažeš s načinom na koji postupamo s tvojim podacima, možeš podnijeti pritužbu tijelu Autoriteit Persoonsgegevens (nizozemskom tijelu za zaštitu podataka) ili nadležnom tijelu u svojoj zemlji.</p>

      <h2>Promjene</h2>
      <p>Ako se nešto promijeni u onome što čuvamo, ažurirat ćemo ovu stranicu. Datum na vrhu pokazuje kada je posljednji put ažurirana.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Pravila privatnosti", description: "Koje podatke Kleurhoek čuva, zašto i koliko dugo: bez kolačića, anonimno brojanje posjeta i računi samo za odrasle.", Body };
