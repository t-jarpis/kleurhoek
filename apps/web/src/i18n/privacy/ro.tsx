import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Ultima actualizare: 4 noiembrie 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be și www.kleurhoek.com) este un site cu planșe de colorat și fișe de lucru manual originale pentru copii. Colectăm cât mai puține date. Pe această pagină îți spunem exact ce păstrăm totuși, de ce, cât timp și ce drepturi ai.</p>

      <h2>Cine suntem</h2>
      <p>Kleurhoek este un site olandez. Pentru întrebări despre confidențialitate, folosește <Link href={contact("privacy")}>formularul de contact</Link>.</p>

      <h2>Vizite și colorat</h2>
      <p>Numărăm vizitele anonim: fără cookie-uri, fără adrese IP și fără nimic ce ar putea duce înapoi la tine. Nu folosim scripturi de publicitate sau de urmărire de la alții, inclusiv de la Google, Meta sau Pinterest. Poți colora, printa și colora împreună cu alții fără cont. Ce colorezi rămâne pe dispozitivul tău. Când colorezi împreună cu alții, liniile trec prin serverul nostru către ceilalți din cameră, fără niciun nume; după 30 de minute fără colorat, camera se închide. Numele pe care le scrii pentru etichetele de cadou nu ajung niciodată pe serverul nostru.</p>
      <p>Ca să nu numărăm vizitatorii de două ori, facem în fiecare zi un cod din adresa ta IP și din browserul tău, cu o cheie care se schimbă zilnic; adresa IP în sine nu o păstrăm. După 90 de zile înlocuim acest cod cu unul aleatoriu, astfel încât nici noi să nu mai putem lega o numărare de un dispozitiv. Numărările în sine (ce pagină, ce țară, telefon sau calculator, când) le păstrăm, ca să vedem cum este folosit site-ul de-a lungul anilor.</p>

      <h2>Cont</h2>
      <p>Conturile sunt doar pentru adulți (de la 16 ani în sus). Copiii nu au nevoie de cont și nu își pot crea unul. Dacă ai un cont, păstrăm numele tău, adresa ta de e-mail și favoritele tale, ca să le găsești pe toate dispozitivele tale. Contul ți-l poți șterge chiar tu; odată cu el se șterg și favoritele și abonarea ta la e-mailuri.</p>

      <h2>E-mail</h2>
      <p>Dacă te abonezi la e-mailuri, păstrăm adresa ta de e-mail, subiectele pe care le alegi, precum și țara și limba ta. Mai întâi confirmi abonarea printr-un link. E-mailurile noastre nu conțin pixeli de urmărire sau linkuri redirecționate prin care să măsurăm dacă le deschizi. Te poți dezabona cu un singur clic în partea de jos a fiecărui e-mail, iar apoi îți ștergem adresa.</p>

      <h2>Contact</h2>
      <p>Dacă ne trimiți un mesaj, folosim numele și adresa ta de e-mail doar ca să-ți răspundem. Păstrăm mesajul cel mult douăsprezece luni.</p>

      <h2>Pinterest, Facebook și Instagram</h2>
      <p>Kleurhoek publică propriile planșe de colorat pe conturile proprii ale Kleurhoek de pe Pinterest, Facebook și Instagram. Pentru asta, conectăm aceste conturi prin autentificarea oficială (OAuth) a Pinterest și Meta. Tokenurile de acces pentru această conexiune le păstrăm criptate și le folosim doar pentru a publica postări și a crea panouri pe propriile noastre conturi. Nu citim, nu colectăm și nu păstrăm date despre alți utilizatori ai acestor servicii și nu folosim conexiunea pentru publicitate. Butonul „Salvează pe Pinterest” de pe site-ul nostru este un simplu link: nu se încarcă niciun script Pinterest. Conexiunea poate fi eliminată oricând, după care ștergem tokenurile.</p>

      <h2>Cine ne ajută</h2>
      <p>Site-ul rulează la Scaleway, în Amsterdam. Cloudflare asigură viteza și securitatea, Zitadel se ocupă de autentificare, iar Brevo trimite e-mailurile noastre. Aceștia prelucrează date doar în numele nostru și doar în acest scop. Dacă dai clic pe un link către un magazin, de exemplu Amazon, din acel moment se aplică politica de confidențialitate a magazinului respectiv.</p>

      <h2>Drepturile tale</h2>
      <p>Poți întreba ce date avem despre tine și poți cere să fie corectate sau șterse. Pentru asta, <Link href={contact("privacy")}>ia legătura cu noi</Link>. Dacă nu ești de acord cu felul în care ne ocupăm de datele tale, poți depune o plângere la Autoriteit Persoonsgegevens (autoritatea olandeză pentru protecția datelor) sau la autoritatea din țara ta.</p>

      <h2>Modificări</h2>
      <p>Dacă se schimbă ceva în ceea ce păstrăm, actualizăm această pagină. Data de sus arată când a fost actualizată ultima dată.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Politica de confidențialitate", description: "Ce date păstrează Kleurhoek, de ce și cât timp: fără cookie-uri, numărare anonimă a vizitelor și conturi doar pentru adulți.", Body };
