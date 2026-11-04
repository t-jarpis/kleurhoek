import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Poslednji put ažurirano 4. novembra 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be i www.kleurhoek.com) je sajt sa originalnim bojankama i listovima za rukotvorine za decu. Prikupljamo što je moguće manje podataka. Na ovoj stranici tačno piše šta ipak čuvamo, zašto, koliko dugo i koja su tvoja prava.</p>

      <h2>Ko smo mi</h2>
      <p>Kleurhoek je holandski sajt. Za pitanja o privatnosti koristi naš <Link href={contact("privacy")}>kontakt formular</Link>.</p>

      <h2>Posećivanje i bojenje</h2>
      <p>Posete brojimo anonimno: bez kolačića, bez IP adresa i bez bilo čega što bi moglo da se poveže s tobom. Ne koristimo skripte za oglašavanje ili praćenje drugih, uključujući one kompanija Google, Meta ili Pinterest. Bojenje, štampanje i zajedničko bojenje mogući su bez naloga. Ono što bojiš ostaje na tvom uređaju. Kada bojite zajedno, potezi idu preko našeg servera do ostalih u sobi, bez imena; ako niko ne boji 30 minuta, soba se zatvara. Imena koja ukucaš za poklon-etikete nikada se ne šalju na naš server.</p>
      <p>Da ne bismo dvaput brojali iste posetioce, svakog dana pravimo kod od tvoje IP adrese i pregledača, pomoću ključa koji se menja svaki dan; samu IP adresu ne čuvamo. Posle 90 dana taj kod zamenjujemo nasumičnim, tako da čak ni mi više ne možemo da povežemo brojanje sa nekim uređajem. Sama brojanja (koja stranica, koja zemlja, telefon ili računar, kada) čuvamo da bismo videli kako se sajt koristi tokom godina.</p>

      <h2>Nalog</h2>
      <p>Nalozi su samo za odrasle (od 16 godina). Deci nalog nije potreban i ne mogu da ga naprave. Ako imaš nalog, čuvamo tvoje ime, imejl adresu i omiljene bojanke, da bi ti bile dostupne na svim tvojim uređajima. Nalog možeš da obrišeš samostalno; s njim se brišu i tvoje omiljene bojanke i prijava za imejlove.</p>

      <h2>Imejl</h2>
      <p>Ako se prijaviš za imejlove, čuvamo tvoju imejl adresu, teme koje izabereš i tvoju zemlju i jezik. Prijavu prvo potvrđuješ preko linka. Naši imejlovi ne sadrže piksele za praćenje niti preusmerene linkove kojima bi se merilo da li ih otvaraš. Odjaviti se možeš jednim klikom na dnu svakog imejla, a tada brišemo tvoju adresu.</p>

      <h2>Kontakt</h2>
      <p>Ako nam pošalješ poruku, tvoje ime i imejl adresu koristimo samo da bismo ti odgovorili. Poruku čuvamo najduže dvanaest meseci.</p>

      <h2>Pinterest, Facebook i Instagram</h2>
      <p>Kleurhoek objavljuje svoje bojanke na sopstvenim Kleurhoek nalozima na mrežama Pinterest, Facebook i Instagram. Za to te naloge povezujemo preko zvanične prijave (OAuth) kompanija Pinterest i Meta. Pristupne tokene za tu vezu čuvamo šifrovane i koristimo ih samo za objavljivanje postova i pravljenje tabli na našim nalozima. Ne čitamo, ne prikupljamo i ne čuvamo podatke o drugim korisnicima tih servisa i ne koristimo vezu za oglašavanje. Dugme „Sačuvaj na Pinterestu“ na našem sajtu je običan link: ne učitava se nikakva Pinterest skripta. Veza može da se ukloni u bilo kom trenutku, nakon čega brišemo tokene.</p>

      <h2>Ko nam pomaže</h2>
      <p>Sajt radi na serverima kompanije Scaleway u Amsterdamu. Cloudflare obezbeđuje brzinu i bezbednost, Zitadel prijavljivanje, a Brevo šalje naše imejlove. One obrađuju podatke samo u naše ime i samo u tu svrhu. Ako klikneš na link ka prodavnici, na primer Amazon, od tog trenutka važi politika privatnosti te prodavnice.</p>

      <h2>Tvoja prava</h2>
      <p>Možeš da pitaš koje podatke o tebi imamo i da tražiš da se isprave ili obrišu. Za to nam se <Link href={contact("privacy")}>javi</Link>. Ako se ne slažeš s načinom na koji postupamo s tvojim podacima, možeš da podneseš pritužbu organu Autoriteit Persoonsgegevens (holandski organ za zaštitu podataka) ili nadzornom organu u svojoj zemlji.</p>

      <h2>Izmene</h2>
      <p>Ako se promeni nešto u onome što čuvamo, ažuriraćemo ovu stranicu. Datum na vrhu pokazuje kada je poslednji put ažurirana.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Politika privatnosti", description: "Koje podatke Kleurhoek čuva, zašto i koliko dugo: bez kolačića, anonimno brojanje poseta i nalozi samo za odrasle.", Body };
