import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Paskutinį kartą atnaujinta 2026 m. lapkričio 4 d.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be ir www.kleurhoek.com) – tai svetainė su originaliais spalvinimo paveikslėliais ir darbelių lapais vaikams. Renkame kuo mažiau duomenų. Šiame puslapyje tiksliai aprašyta, ką vis dėlto saugome, kodėl, kiek laiko ir kokios yra tavo teisės.</p>

      <h2>Kas mes esame</h2>
      <p>Kleurhoek – Nyderlandų svetainė. Jei turi klausimų apie privatumą, naudokis mūsų <Link href={contact("privacy")}>kontaktų forma</Link>.</p>

      <h2>Lankymasis ir spalvinimas</h2>
      <p>Apsilankymus skaičiuojame anonimiškai: be slapukų, be IP adresų ir be nieko, pagal ką būtų galima tave atsekti. Nenaudojame kitų reklamos ar sekimo scenarijų, taip pat ir Google, Meta ar Pinterest. Spalvinti, spausdinti ir spalvinti kartu galima be paskyros. Tai, ką spalvini, lieka tavo įrenginyje. Kai spalvinate kartu, potėpiai per mūsų serverį perduodami kitiems kambaryje esantiems, be jokių vardų; jei 30 minučių niekas nespalvina, kambarys uždaromas. Vardai, kuriuos įvedi dovanų etiketėms, niekada nesiunčiami į mūsų serverį.</p>
      <p>Kad tų pačių lankytojų nesuskaičiuotume du kartus, kiekvieną dieną iš tavo IP adreso ir naršyklės sukuriame kodą, naudodami kasdien besikeičiantį raktą; paties IP adreso nesaugome. Po 90 dienų tą kodą pakeičiame atsitiktiniu, kad net mes nebegalėtume susieti skaičiavimo su įrenginiu. Pačius skaičiavimus (kuris puslapis, kuri šalis, telefonas ar kompiuteris, kada) saugome, kad matytume, kaip svetainė naudojama bėgant metams.</p>

      <h2>Paskyra</h2>
      <p>Paskyros skirtos tik suaugusiesiems (16 metų ir vyresniems). Vaikams paskyros nereikia, ir jie negali jos susikurti. Jei turi paskyrą, saugome tavo vardą, el. pašto adresą ir mėgstamiausius paveikslėlius, kad galėtum juos rasti visuose savo įrenginiuose. Paskyrą gali ištrinti savarankiškai; kartu su ja ištrinami ir tavo mėgstamiausi paveikslėliai bei el. laiškų prenumerata.</p>

      <h2>El. laiškai</h2>
      <p>Jei užsiprenumeruoji el. laiškus, saugome tavo el. pašto adresą, pasirinktas temas, taip pat tavo šalį ir kalbą. Pirmiausia prenumeratą patvirtini per nuorodą. Mūsų laiškuose nėra sekimo pikselių ar peradresuojamų nuorodų, kuriomis būtų matuojama, ar juos atidarai. Atsisakyti prenumeratos gali vienu paspaudimu kiekvieno laiško apačioje, ir tada ištriname tavo adresą.</p>

      <h2>Kontaktai</h2>
      <p>Jei atsiunti mums žinutę, tavo vardą ir el. pašto adresą naudojame tik tam, kad tau atsakytume. Žinutę saugome ne ilgiau kaip dvylika mėnesių.</p>

      <h2>Pinterest, Facebook ir Instagram</h2>
      <p>Kleurhoek skelbia savo spalvinimo paveikslėlius nuosavose Kleurhoek paskyrose Pinterest, Facebook ir Instagram platformose. Tam šias paskyras susiejame per oficialų Pinterest ir Meta prisijungimą (OAuth). Šio susiejimo prieigos raktus saugome užšifruotus ir naudojame tik įrašams skelbti ir lentoms kurti savo paskyrose. Neskaitome, nerenkame ir nesaugome kitų šių paslaugų naudotojų duomenų ir nenaudojame susiejimo reklamai. Mygtukas „Išsaugoti „Pinterest““ mūsų svetainėje yra paprasta nuoroda: jokie Pinterest scenarijai neįkeliami. Susiejimą galima bet kada pašalinti, o tada prieigos raktus ištriname.</p>

      <h2>Kas mums padeda</h2>
      <p>Svetainė veikia Scaleway serveriuose Amsterdame. Cloudflare užtikrina spartą ir saugumą, Zitadel – prisijungimą, o Brevo siunčia mūsų el. laiškus. Jie tvarko duomenis tik mūsų vardu ir tik šiam tikslui. Jei spusteli nuorodą į parduotuvę, pavyzdžiui, Amazon, nuo tos akimirkos galioja tos parduotuvės privatumo politika.</p>

      <h2>Tavo teisės</h2>
      <p>Gali paklausti, kokius duomenis apie tave turime, ir paprašyti juos ištaisyti arba ištrinti. Tam <Link href={contact("privacy")}>susisiek su mumis</Link>. Jei nesutinki su tuo, kaip tvarkome tavo duomenis, gali pateikti skundą institucijai Autoriteit Persoonsgegevens (Nyderlandų duomenų apsaugos institucija) arba savo šalies priežiūros institucijai.</p>

      <h2>Pakeitimai</h2>
      <p>Jei pasikeičia tai, ką saugome, atnaujiname šį puslapį. Data viršuje rodo, kada jis paskutinį kartą buvo atnaujintas.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Privatumo politika", description: "Kokius duomenis Kleurhoek saugo, kodėl ir kiek laiko: jokių slapukų, anoniminis apsilankymų skaičiavimas ir paskyros tik suaugusiesiems.", Body };
