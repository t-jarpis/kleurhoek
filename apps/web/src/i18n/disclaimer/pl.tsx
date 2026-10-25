import Link from "next/link";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Pools (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ market, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Ostatnia aktualizacja: 24 października 2026 r.</p>
      <p>Na tej stronie przeczytasz, co możesz robić z kolorowankami i planszami do wycinania z Kleurhoek, jak linkujemy do innych stron internetowych i jak możesz nam coś zgłosić. Korzystając z Kleurhoek, akceptujesz te zasady.</p>

      <h2>Wszystko narysowaliśmy sami</h2>
      <p>Wszystkie kolorowanki, wycinanki i modele z papieru w Kleurhoek zostały narysowane specjalnie dla Kleurhoek. Nie kopiujemy rysunków z innych stron internetowych ani z książek i nie odrysowujemy znanych postaci, marek ani bohaterów. Prawa autorskie do rysunków i do tej strony należą do Kleurhoek.</p>
      <p>Z plansz możesz korzystać bezpłatnie:</p>
      <ul>
        <li>w domu, aby je kolorować, drukować i rozdawać rodzinie i przyjaciołom;</li>
        <li>w szkole, w żłobku, przedszkolu lub świetlicy, w stowarzyszeniu albo w bibliotece, także w dużych ilościach;</li>
        <li>na przyjęciu, na przykład jako zajęcia plastyczne.</li>
      </ul>
      <p>Bez naszej pisemnej zgody nie wolno: sprzedawać plansz (pojedynczo, w zeszycie ani do pobrania), publikować ich jako własnych materiałów na innej stronie internetowej, w aplikacji lub w mediach społecznościowych ani wykorzystywać ich w produktach lub reklamach. Udostępniać możesz natomiast link do planszy w Kleurhoek.</p>

      <h2>Motywy u twórców</h2>
      <p>Dzieci często szukają kolorowanek z postaciami z filmów animowanych, parków rozrywki lub książek. Te rysunki należą do ich twórców i nie możemy ich sami rysować ani kopiować. Wielu twórców udostępnia je jednak bezpłatnie na własnej stronie. W dziale <Link href={`/${market}/themas`}>Motywy u twórców</Link> zbieramy linki do tych stron. Obowiązują przy tym następujące zasady:</p>
      <ul>
        <li>Linkujemy wyłącznie do oficjalnej strony twórcy lub właściciela praw, nigdy do stron, które przejmują rysunki innych.</li>
        <li>Nie pokazujemy obrazów, rysunków ani logo twórcy i ich nie przechowujemy. U nas widzisz tylko nasz własny opis i link. Może być inaczej tylko wtedy, gdy twórca udzieli nam na to pisemnej zgody; wtedy jest to wyraźnie zaznaczone.</li>
        <li>Każdy link sprawdzamy, zanim pojawi się w serwisie. Następnie program komputerowy codziennie sprawdza, czy strona nadal istnieje. Jeśli strona zniknie, automatycznie usuwamy link. Zawsze przestrzegamy przy tym zasad (robots.txt) strony twórcy.</li>
        <li>Za treść stron twórców odpowiadają oni sami i obowiązują na nich ich własne warunki. Nie mamy na nie wpływu.</li>
      </ul>
      <p>Jesteś twórcą i chcesz, żebyśmy zmienili lub usunęli link, albo chcesz z nami współpracować? <Link href={contact("partnership")}>Skontaktuj się z nami</Link>. Wprowadzimy zmianę w ciągu pięciu dni roboczych.</p>

      <h2>Marki i nazwy</h2>
      <p>Nazwy postaci, parków rozrywki, seriali i marek należą do ich właścicieli. Używamy ich wyłącznie po to, by opisać, gdzie można coś znaleźć. Kleurhoek nie jest powiązany z tymi właścicielami i nie jest przez nich sponsorowany, chyba że zostało to wyraźnie zaznaczone.</p>

      <h2>Linki partnerskie</h2>
      <p>Przy niektórych planszach i motywach wymieniamy przybory, których możesz przy nich użyć, na przykład nożyczki dla dzieci albo kredki. To linki partnerskie: jeśli kupisz coś przez taki link, Kleurhoek dostaje od sklepu niewielkie wynagrodzenie. Ty płacisz tyle samo. Dzięki temu plansze pozostają darmowe. Linki partnerskie są zawsze wyraźnie oznaczone. Za produkt, cenę i dostawę odpowiada sklep.</p>

      <h2>Zgłaszanie naruszeń praw autorskich</h2>
      <p>Uważasz, że w Kleurhoek jest coś, do czego prawa należą do ciebie, albo że link prowadzi do czegoś, co nie powinno być udostępniane? Zgłoś to przez <Link href={contact("copyright")}>formularz kontaktowy</Link>, wybierając temat &quot;Prawa autorskie&quot;. Podaj, której strony to dotyczy, dlaczego twoim zdaniem coś jest nie w porządku i jak możemy się z tobą skontaktować. Odpowiadamy w ciągu pięciu dni roboczych, a jeśli jest ku temu powód, usuwamy materiał na czas wyjaśniania sprawy.</p>

      <h2>Bezpieczne prace plastyczne</h2>
      <p>Wycinanki i modele z papieru są przeznaczone do wykonywania razem z osobą dorosłą. Używaj nożyczek dla dzieci, a w lampionach zawsze lampki LED, nigdy prawdziwej świecy. Małe elementy nie są odpowiednie dla dzieci poniżej trzech lat.</p>

      <h2>Odpowiedzialność</h2>
      <p>Tworzymy Kleurhoek z dużą starannością, ale nie możemy obiecać, że wszystko będzie zawsze bezbłędne ani że strona będzie zawsze dostępna. W zakresie dozwolonym przez prawo Kleurhoek nie ponosi odpowiedzialności za szkody wynikające z korzystania ze strony, z plansz lub ze stron, do których linkujemy.</p>

      <h2>Prywatność</h2>
      <p>Odwiedziny liczymy anonimowo: bez plików cookie, bez adresu IP i bez niczego, co pozwalałoby cię zidentyfikować. Do kolorowania i drukowania konto nie jest potrzebne. Jeśli je założysz, przechowujemy twoje imię, adres e-mail i ulubione, żebyś znalazł je na wszystkich swoich urządzeniach; konto możesz w każdej chwili sam usunąć. Jeśli zapiszesz się na e-maile, używamy twojego adresu tylko do tego, a wypisanie się go usuwa. Jeśli wyślesz nam wiadomość, użyjemy twojego imienia i adresu e-mail wyłącznie po to, by ci odpowiedzieć, a wiadomość przechowujemy najwyżej dwanaście miesięcy. Chcesz, żebyśmy usunęli twoją wiadomość wcześniej? <Link href={contact("privacy")}>Daj nam znać</Link>.</p>

      <h2>Zmiany i pytania</h2>
      <p>Możemy zmieniać te zastrzeżenia, na przykład gdy w Kleurhoek pojawi się coś nowego. Na górze strony podajemy datę ostatniej aktualizacji. Te zastrzeżenia podlegają prawu holenderskiemu. Masz pytania? <Link href={contact()}>Skontaktuj się z nami</Link>.</p>
    </>
  );
}
