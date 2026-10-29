import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Lithuanian (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Paskutinį kartą atnaujinta 2026 m. spalio 24 d.</p>
      <p>Šiame puslapyje paaiškinama, ką galima daryti su Kleurhoek spalvinimo paveikslėliais ir darbelių lapais, kaip pateikiame nuorodas į kitas svetaines ir kaip mums ką nors pranešti. Naudodamasis Kleurhoek, sutinki su šiomis sąlygomis.</p>

      <h2>Mūsų pačių kūriniai</h2>
      <p>Visi Kleurhoek spalvinimo paveikslėliai, iškarpos ir popieriniai modeliai sukurti specialiai Kleurhoek. Kuriame juos padedami dirbtinio intelekto ir kiekvieną paveikslėlį patikriname prieš jį paskelbdami. Nieko nekopijuojame iš kitų svetainių ar knygų ir neatkuriame žinomų personažų, prekės ženklų ar figūrų. Svetainė, Kleurhoek pavadinimas ir paveikslėlių kolekcija priklauso Kleurhoek.</p>
      <p>Paveikslėlius gali naudoti nemokamai:</p>
      <ul>
        <li>namuose – spalvinti, spausdinti ir dalyti šeimai bei draugams;</li>
        <li>mokykloje, darželyje, būrelyje ar bibliotekoje, taip pat ir dideliais kiekiais;</li>
        <li>šventėje, pavyzdžiui, kaip darbelių užsiėmimą.</li>
      </ul>
      <p>Be mūsų rašytinio leidimo draudžiama: parduoti paveikslėlius (atskirai, knygelėje ar kaip atsisiunčiamą failą), skelbti juos kitoje svetainėje, programėlėje ar socialiniuose tinkluose kaip savo medžiagą arba naudoti juos produktuose ar reklamoje. Nuorodą į puslapį Kleurhoek svetainėje dalytis visada galima.</p>

      <h2>Temos iš kūrėjų</h2>
      <p>Vaikai dažnai ieško spalvinimo paveikslėlių su animacinių filmų, pramogų parkų ar knygų personažais. Tie piešiniai priklauso jų kūrėjams, ir mums neleidžiama patiems jų kurti ar kopijuoti. Tačiau daugelis kūrėjų juos nemokamai siūlo savo svetainėse. Skiltyje <Link href={link(base, "/themas")}>Temos iš kūrėjų</Link> renkame nuorodas į tuos puslapius. Galioja šios taisyklės:</p>
      <ul>
        <li>Pateikiame nuorodas tik į oficialią kūrėjo ar teisių turėtojo svetainę, niekada į svetaines, kurios kopijuoja kitų piešinius.</li>
        <li>Nerodome ir nesaugome jokių kūrėjo paveikslėlių, piešinių ar logotipų. Mūsų svetainėje matai tik mūsų pačių aprašymą ir nuorodą. Išimtis galima tik tada, kai kūrėjas mums duoda rašytinį leidimą, ir tokiu atveju tai nurodome.</li>
        <li>Prieš paskelbdami patikriname kiekvieną nuorodą. Vėliau kompiuterinė programa kasdien tikrina, ar puslapis dar egzistuoja. Jei puslapis dingsta, nuorodą pašaliname automatiškai. Tai darydami visada laikomės kūrėjo svetainės taisyklių (robots.txt).</li>
        <li>Už kūrėjų svetainių turinį atsako patys kūrėjai, ir jam taikomos jų pačių sąlygos. Mes jo nekontroliuojame.</li>
      </ul>
      <p>Esi kūrėjas ir nori, kad pakeistume ar pašalintume nuorodą, arba norėtum su mumis bendradarbiauti? <Link href={contact("partnership")}>Susisiek su mumis</Link>. Pakeitimą atliksime per penkias darbo dienas.</p>

      <h2>Prekės ženklai ir pavadinimai</h2>
      <p>Personažų, pramogų parkų, serialų ir prekės ženklų pavadinimai priklauso jų savininkams. Juos naudojame tik tam, kad nurodytume, kur ką galima rasti. Kleurhoek nėra susijęs su šiais savininkais ir jų neremiamas, nebent tai aiškiai nurodyta.</p>

      <h2>Partnerių nuorodos</h2>
      <p>Prie kai kurių paveikslėlių ir temų paminime daiktus, kuriuos galima su jais naudoti, pavyzdžiui, vaikiškas žirkles ar spalvotus pieštukus. Tai partnerių nuorodos: jei per tokią nuorodą ką nors nusiperki, Kleurhoek gauna nedidelį atlygį iš parduotuvės. Tu moki tiek pat. Taip paveikslėliai lieka nemokami. Partnerių nuorodos visada aiškiai pažymėtos. Už prekę, kainą ir pristatymą atsako parduotuvė.</p>

      <h2>Pranešimas apie autorių teises</h2>
      <p>Manai, kad Kleurhoek svetainėje yra kažkas, į ką teisės priklauso tau, arba kad kokia nors nuoroda veda ten, kur neturėtų? Pranešk apie tai per <Link href={contact("copyright")}>kontaktų formą</Link>, pasirinkęs temą &quot;Autorių teisės&quot;. Nurodyk, apie kurį puslapį kalbama, kodėl manai, kad kažkas negerai, ir kaip su tavimi susisiekti. Atsakysime per penkias darbo dienas ir, jei bus pagrindo, pašalinsime turinį, kol situaciją išsiaiškinsime.</p>

      <h2>Saugūs darbeliai</h2>
      <p>Iškarpos ir popieriniai modeliai skirti gaminti kartu su suaugusiuoju. Naudok vaikiškas žirkles, o žibintuose visada naudok LED lemputę, niekada tikros žvakės. Smulkios dalys netinka vaikams iki trejų metų.</p>

      <h2>Atsakomybė</h2>
      <p>Kleurhoek kuriame labai kruopščiai, tačiau negalime pažadėti, kad viskas visada bus be klaidų ar kad svetainė visada bus pasiekiama. Kiek leidžia įstatymai, Kleurhoek neatsako už žalą, atsiradusią naudojantis svetaine, paveikslėliais ar svetainėmis, į kurias pateikiame nuorodas.</p>

      <h2>Privatumas</h2>
      <p>Apsilankymus skaičiuojame anonimiškai: be slapukų, be IP adresų ir be nieko, kas galėtų būti susieta su tavimi. Norint spalvinti ar spausdinti, paskyros nereikia. Jei vis dėlto ją susikuri, saugome tavo vardą, el. pašto adresą ir mėgstamiausius, kad juos rastum visuose savo įrenginiuose; paskyrą gali bet kada ištrinti pats. Jei užsiprenumeruoji laiškus, tavo adresą naudojame tik tam, o atsisakius prenumeratos jis ištrinamas. Jei atsiunti mums žinutę, tavo vardą ir el. pašto adresą naudojame tik tam, kad tau atsakytume, o žinutę saugome ne ilgiau kaip dvylika mėnesių. Nori, kad žinutę ištrintume anksčiau? <Link href={contact("privacy")}>Pranešk mums</Link>.</p>

      <h2>Pakeitimai ir klausimai</h2>
      <p>Šią informaciją galime keisti, pavyzdžiui, kai Kleurhoek atsiranda kažkas naujo. Data viršuje rodo, kada ji paskutinį kartą atnaujinta. Šiai informacijai taikoma Nyderlandų teisė. Turi klausimų? <Link href={contact()}>Susisiek su mumis</Link>.</p>
    </>
  );
}
