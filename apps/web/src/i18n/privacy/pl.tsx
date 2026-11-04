import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Ostatnia aktualizacja: 4 listopada 2026 r.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be i www.kleurhoek.com) to strona internetowa z własnymi kolorowankami i planszami do prac plastycznych dla dzieci. Zbieramy jak najmniej danych. Na tej stronie dokładnie opisujemy, co jednak przechowujemy, dlaczego, jak długo i jakie masz prawa.</p>

      <h2>Kim jesteśmy</h2>
      <p>Kleurhoek to niderlandzka strona internetowa. W sprawach prywatności skorzystaj z naszego <Link href={contact("privacy")}>formularza kontaktowego</Link>.</p>

      <h2>Odwiedziny i kolorowanie</h2>
      <p>Odwiedziny liczymy anonimowo: bez plików cookie, bez adresów IP i bez niczego, co dałoby się powiązać z tobą. Nie używamy skryptów reklamowych ani śledzących innych firm, w tym Google, Meta czy Pinterest. Kolorować, drukować i kolorować razem możesz bez konta. To, co kolorujesz, zostaje na twoim urządzeniu. Gdy kolorujesz razem z innymi, pociągnięcia przechodzą przez nasz serwer do pozostałych osób w pokoju, bez żadnych imion; po 30 minutach bez kolorowania pokój zostaje zamknięty. Imiona wpisywane na etykietach prezentowych nigdy nie trafiają na nasz serwer.</p>
      <p>Aby nie liczyć odwiedzających podwójnie, codziennie tworzymy kod z twojego adresu IP i przeglądarki, używając klucza, który zmienia się każdego dnia; samego adresu IP nie zapisujemy. Po 90 dniach zastępujemy ten kod losowym, tak że nawet my nie możemy już powiązać danego zliczenia z urządzeniem. Same zliczenia (która strona, jaki kraj, telefon czy komputer, kiedy) przechowujemy, aby widzieć, jak strona jest używana na przestrzeni lat.</p>

      <h2>Konto</h2>
      <p>Konta są tylko dla dorosłych (w wieku 16 lat lub więcej). Dzieci nie potrzebują konta i nie mogą go założyć. Jeśli masz konto, przechowujemy twoje imię, adres e-mail i ulubione, aby były dostępne na wszystkich twoich urządzeniach. Konto możesz usunąć samodzielnie; razem z nim usuwane są twoje ulubione i zapis na e-maile.</p>

      <h2>E-mail</h2>
      <p>Jeśli zapiszesz się na e-maile, przechowujemy twój adres e-mail, wybrane przez ciebie tematy oraz twój kraj i język. Najpierw potwierdzasz zapis, klikając link. Nasze e-maile nie zawierają pikseli śledzących ani przekierowanych linków, które mierzyłyby, czy je otwierasz. Wypisać się możesz jednym kliknięciem na dole każdego e-maila, a wtedy usuwamy twój adres.</p>

      <h2>Kontakt</h2>
      <p>Jeśli wyślesz nam wiadomość, twojego imienia i adresu e-mail używamy tylko do odpowiedzi. Wiadomość przechowujemy najwyżej dwanaście miesięcy.</p>

      <h2>Pinterest, Facebook i Instagram</h2>
      <p>Kleurhoek publikuje własne kolorowanki na własnych kontach Kleurhoek w serwisach Pinterest, Facebook i Instagram. W tym celu łączymy te konta przez oficjalne logowanie (OAuth) serwisów Pinterest i Meta. Tokeny dostępu do tego połączenia przechowujemy w postaci zaszyfrowanej i używamy ich wyłącznie do publikowania postów i tworzenia tablic na naszych własnych kontach. Nie odczytujemy, nie zbieramy ani nie przechowujemy danych innych użytkowników tych serwisów i nie używamy tego połączenia do reklam. Przycisk „Zapisz na Pintereście” na naszej stronie to zwykły link: nie jest ładowany żaden skrypt serwisu Pinterest. Połączenie można w każdej chwili usunąć, a wtedy usuwamy tokeny.</p>

      <h2>Kto nam pomaga</h2>
      <p>Strona działa na serwerach Scaleway w Amsterdamie. Cloudflare zapewnia szybkość i bezpieczeństwo, Zitadel obsługuje logowanie, a Brevo wysyła nasze e-maile. Przetwarzają one dane wyłącznie w naszym imieniu i tylko w tym celu. Jeśli klikniesz link do sklepu, na przykład Amazon, od tej chwili obowiązuje polityka prywatności tego sklepu.</p>

      <h2>Twoje prawa</h2>
      <p>Możesz zapytać, jakie dane o tobie mamy, oraz poprosić o ich poprawienie lub usunięcie. W tym celu <Link href={contact("privacy")}>skontaktuj się z nami</Link>. Jeśli nie zgadzasz się ze sposobem, w jaki postępujemy z twoimi danymi, możesz złożyć skargę do Autoriteit Persoonsgegevens (niderlandzkiego organu ochrony danych osobowych) lub do organu w twoim kraju.</p>

      <h2>Zmiany</h2>
      <p>Jeśli coś się zmieni w tym, co przechowujemy, zaktualizujemy tę stronę. Data na górze pokazuje, kiedy była ostatnio aktualizowana.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Polityka prywatności", description: "Jakie dane przechowuje Kleurhoek, dlaczego i jak długo: bez plików cookie, anonimowe liczenie odwiedzin i konta tylko dla dorosłych.", Body };
