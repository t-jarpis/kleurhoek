import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Përditësuar së fundi më 4 nëntor 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be dhe www.kleurhoek.com) është një faqe interneti me fletë origjinale për ngjyrosje dhe fletë për punë dore për fëmijë. Mbledhim sa më pak të dhëna të jetë e mundur. Në këtë faqe shpjegohet saktësisht çfarë ruajmë, pse, për sa kohë dhe cilat janë të drejtat e tua.</p>

      <h2>Kush jemi</h2>
      <p>Kleurhoek është një faqe interneti holandeze. Për pyetje rreth privatësisë, të lutem përdor <Link href={contact("privacy")}>formularin tonë të kontaktit</Link>.</p>

      <h2>Vizitat dhe ngjyrosja</h2>
      <p>Vizitat i numërojmë në mënyrë anonime: pa cookies, pa adresa IP dhe pa asgjë që mund të të lidhë me ty. Nuk përdorim skripte reklamash apo gjurmimi nga të tjerë, as nga Google, Meta apo Pinterest. Mund të ngjyrosësh, të printosh dhe të ngjyrosësh së bashku pa llogari. Ajo që ngjyros mbetet në pajisjen tënde. Kur ngjyrosni së bashku, vijat kalojnë përmes serverit tonë te të tjerët në dhomë, pa emra; nëse askush nuk ngjyros për 30 minuta, dhoma mbyllet. Emrat që shkruan për etiketat e dhuratave nuk dërgohen kurrë në serverin tonë.</p>
      <p>Për të mos i numëruar vizitorët dy herë, çdo ditë krijojmë një kod nga adresa jote IP dhe shfletuesi, me një çelës që ndryshon çdo ditë; vetë adresën IP nuk e ruajmë. Pas 90 ditësh e zëvendësojmë atë kod me një kod të rastësishëm, që as ne të mos mund ta lidhim më një numërim me një pajisje. Vetë numërimet (cila faqe, cili vend, telefon apo kompjuter, kur) i ruajmë, që të shohim si përdoret faqja ndër vite.</p>

      <h2>Llogaria</h2>
      <p>Llogaritë janë vetëm për të rriturit (16 vjeç e lart). Fëmijët nuk kanë nevojë për llogari dhe nuk mund të krijojnë një të tillë. Nëse ke llogari, ruajmë emrin tënd, adresën tënde të email-it dhe të preferuarat e tua, që t&apos;i gjesh në të gjitha pajisjet e tua. Llogarinë mund ta fshish vetë; bashkë me të fshihen edhe të preferuarat e tua dhe regjistrimi për email-e.</p>

      <h2>Email</h2>
      <p>Nëse regjistrohesh për email-e, ruajmë adresën tënde të email-it, temat që zgjedh, si dhe vendin dhe gjuhën tënde. Fillimisht e konfirmon regjistrimin përmes një lidhjeje. Email-et tona nuk përmbajnë piksele gjurmimi apo lidhje të ridrejtuara për të matur nëse i hap. Mund të çregjistrohesh me një klikim në fund të çdo email-i, dhe atëherë e fshijmë adresën tënde.</p>

      <h2>Kontakti</h2>
      <p>Nëse na dërgon një mesazh, emrin dhe adresën tënde të email-it i përdorim vetëm për të të përgjigjur. Mesazhin e ruajmë jo më shumë se dymbëdhjetë muaj.</p>

      <h2>Pinterest, Facebook dhe Instagram</h2>
      <p>Kleurhoek publikon fletët e veta për ngjyrosje në llogaritë e veta të Kleurhoek në Pinterest, Facebook dhe Instagram. Për këtë, i lidhim këto llogari përmes hyrjes zyrtare (OAuth) të Pinterest dhe Meta. Tokenët e qasjes për këtë lidhje i ruajmë të enkriptuar dhe i përdorim vetëm për të publikuar postime dhe për të krijuar tabela në llogaritë tona. Nuk lexojmë, nuk mbledhim dhe nuk ruajmë të dhëna për përdorues të tjerë të këtyre shërbimeve dhe nuk e përdorim lidhjen për reklama. Butoni „Ruaje në Pinterest“ në faqen tonë është një lidhje e thjeshtë: nuk ngarkohet asnjë skript i Pinterest. Lidhja mund të hiqet në çdo kohë, pas së cilës i fshijmë tokenët.</p>

      <h2>Kush na ndihmon</h2>
      <p>Faqja e internetit funksionon në serverët e Scaleway në Amsterdam. Cloudflare siguron shpejtësinë dhe sigurinë, Zitadel menaxhon hyrjen dhe Brevo dërgon email-et tona. Ata i përpunojnë të dhënat vetëm në emrin tonë dhe vetëm për këtë qëllim. Nëse klikon një lidhje për në një dyqan, si Amazon, nga ai moment vlen politika e privatësisë e atij dyqani.</p>

      <h2>Të drejtat e tua</h2>
      <p>Mund të pyesësh cilat të dhëna kemi për ty dhe të kërkosh që të korrigjohen ose të fshihen. Për këtë, <Link href={contact("privacy")}>na kontakto</Link>. Nëse nuk je dakord me mënyrën si i trajtojmë të dhënat e tua, mund të paraqesësh ankesë te Autoriteit Persoonsgegevens (autoriteti holandez për mbrojtjen e të dhënave) ose te autoriteti mbikëqyrës në vendin tënd.</p>

      <h2>Ndryshimet</h2>
      <p>Nëse ndryshon diçka në atë që ruajmë, e përditësojmë këtë faqe. Data në krye tregon kur është përditësuar për herë të fundit.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Politika e privatësisë", description: "Cilat të dhëna ruan Kleurhoek, pse dhe për sa kohë: pa cookies, numërim anonim i vizitave dhe llogari vetëm për të rriturit.", Body };
