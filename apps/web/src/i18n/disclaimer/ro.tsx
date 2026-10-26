import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Roemeens (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Ultima actualizare: 24 octombrie 2026.</p>
      <p>Această pagină explică ce ai voie să faci cu planșele de colorat și fișele de lucru manual de pe Kleurhoek, cum trimitem către alte site-uri și cum ne poți semnala ceva. Folosind Kleurhoek, ești de acord cu aceste condiții.</p>

      <h2>Creațiile noastre</h2>
      <p>Toate planșele de colorat, decupajele și machetele din hârtie de pe Kleurhoek sunt create special pentru Kleurhoek. Le realizăm cu ajutorul inteligenței artificiale și verificăm fiecare planșă înainte să apară online. Nu copiem nimic de pe alte site-uri sau din cărți și nu reproducem personaje, mărci sau figuri cunoscute. Site-ul, numele Kleurhoek și colecția de planșe aparțin Kleurhoek.</p>
      <p>Poți folosi planșele gratuit:</p>
      <ul>
        <li>acasă, ca să le colorezi, să le printezi și să le dai familiei și prietenilor;</li>
        <li>la școală, la grădiniță, la un club sau la bibliotecă, inclusiv în număr mare;</li>
        <li>la o petrecere, de exemplu ca activitate de lucru manual.</li>
      </ul>
      <p>Fără acordul nostru scris nu este permis: să vinzi planșele (separat, într-o broșură sau ca descărcare), să le pui pe alt site, într-o aplicație sau pe rețelele sociale ca material propriu ori să le folosești în produse sau în publicitate. Poți oricând să distribui un link către pagina de pe Kleurhoek.</p>

      <h2>Teme de la creatori</h2>
      <p>Copiii caută adesea planșe de colorat cu personaje din desene animate, dintr-un parc de distracții sau dintr-o carte. Acele desene aparțin creatorilor lor, iar noi nu avem voie să le facem sau să le copiem. Dar mulți creatori le oferă gratuit pe propriile site-uri. La <Link href={link(base, "/themas")}>Teme de la creatori</Link> adunăm linkuri către acele pagini. Se aplică următoarele:</p>
      <ul>
        <li>Trimitem doar către site-ul oficial al creatorului sau al deținătorului drepturilor, niciodată către site-uri care copiază desenele altora.</li>
        <li>Nu afișăm și nu păstrăm imagini, desene sau logouri ale creatorului. Pe site-ul nostru vezi doar descrierea noastră și un link. Poate fi altfel numai dacă un creator ne dă acordul scris, iar în acel caz o spunem.</li>
        <li>Verificăm fiecare link înainte să apară online. Apoi, un program verifică zilnic dacă pagina mai există. Dacă o pagină dispare, eliminăm linkul automat. Respectăm întotdeauna regulile (robots.txt) ale site-ului creatorului.</li>
        <li>Conținutul site-urilor creatorilor este responsabilitatea lor și se supune propriilor lor condiții. Nu avem niciun control asupra lui.</li>
      </ul>
      <p>Ești creator și vrei să modificăm sau să eliminăm un link ori vrei să colaborezi cu noi? <Link href={contact("partnership")}>Contactează-ne</Link>. Facem modificarea în cel mult cinci zile lucrătoare.</p>

      <h2>Mărci și nume</h2>
      <p>Numele personajelor, parcurilor de distracții, serialelor și mărcilor aparțin proprietarilor lor. Le folosim doar ca să descriem unde poți găsi ceva. Kleurhoek nu este afiliat acestor proprietari și nu este sponsorizat de ei, cu excepția cazului în care se precizează explicit.</p>

      <h2>Linkuri de partener</h2>
      <p>La unele planșe și teme menționăm lucruri pe care le poți folosi, de exemplu foarfece pentru copii sau creioane colorate. Acestea sunt linkuri de partener: dacă cumperi ceva printr-un astfel de link, Kleurhoek primește un mic comision de la magazin. Tu plătești la fel. Așa planșele rămân gratuite. Linkurile de partener sunt întotdeauna marcate clar. Magazinul răspunde de produs, de preț și de livrare.</p>

      <h2>Semnalarea drepturilor de autor</h2>
      <p>Crezi că pe Kleurhoek există ceva asupra căruia deții drepturile sau că un link trimite către ceva nepotrivit? Semnalează-ne prin <Link href={contact("copyright")}>formularul de contact</Link>, cu subiectul „Drepturi de autor”. Spune-ne despre ce pagină este vorba, de ce crezi că nu e în regulă și cum te putem contacta. Răspundem în cel mult cinci zile lucrătoare și, dacă există motive, eliminăm conținutul cât timp verificăm.</p>

      <h2>Lucru manual în siguranță</h2>
      <p>Decupajele și machetele din hârtie sunt făcute pentru a fi realizate împreună cu un adult. Folosește foarfece pentru copii, iar pentru felinare folosește întotdeauna o lumină LED, niciodată o lumânare adevărată. Piesele mici nu sunt potrivite pentru copiii sub trei ani.</p>

      <h2>Răspundere</h2>
      <p>Facem Kleurhoek cu multă grijă, dar nu putem promite că totul este mereu fără greșeli sau că site-ul este mereu disponibil. În măsura permisă de lege, Kleurhoek nu răspunde pentru niciun prejudiciu rezultat din folosirea site-ului, a planșelor sau a site-urilor către care trimitem.</p>

      <h2>Confidențialitate</h2>
      <p>Numărăm vizitele anonim: fără cookie-uri, fără adrese IP și fără nimic ce te-ar putea identifica. Nu ai nevoie de cont ca să colorezi sau să printezi. Dacă îți faci totuși unul, păstrăm numele tău, adresa ta de e-mail și favoritele tale, ca să le găsești pe toate dispozitivele; îți poți șterge oricând singur contul. Dacă te abonezi la e-mailuri, folosim adresa ta doar pentru asta, iar dezabonarea o șterge. Dacă ne trimiți un mesaj, folosim numele și adresa ta de e-mail doar ca să-ți răspundem și păstrăm mesajul cel mult douăsprezece luni. Vrei să-ți ștergem mesajul mai devreme? <Link href={contact("privacy")}>Spune-ne</Link>.</p>

      <h2>Modificări și întrebări</h2>
      <p>Putem modifica aceste mențiuni legale, de exemplu când apare ceva nou pe Kleurhoek. Data de sus arată când au fost actualizate ultima dată. Acestor mențiuni legale li se aplică legea olandeză. Ai întrebări? <Link href={contact()}>Contactează-ne</Link>.</p>
    </>
  );
}
