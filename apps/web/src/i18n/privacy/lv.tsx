import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Pēdējoreiz atjaunināts 2026. gada 4. novembrī.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be un www.kleurhoek.com) ir tīmekļa vietne ar oriģinālām krāsojamām lapām un rokdarbu lapām bērniem. Mēs vācam pēc iespējas mazāk datu. Šajā lapā ir precīzi aprakstīts, ko mēs tomēr glabājam, kāpēc, cik ilgi un kādas ir tavas tiesības.</p>

      <h2>Kas mēs esam</h2>
      <p>Kleurhoek ir Nīderlandes tīmekļa vietne. Ar jautājumiem par privātumu, lūdzu, izmanto mūsu <Link href={contact("privacy")}>saziņas veidlapu</Link>.</p>

      <h2>Apmeklēšana un krāsošana</h2>
      <p>Mēs skaitām apmeklējumus anonīmi: bez sīkdatnēm, bez IP adresēm un bez nekā, ko varētu saistīt ar tevi. Mēs neizmantojam citu reklāmas vai izsekošanas skriptus, arī ne Google, Meta vai Pinterest skriptus. Krāsot, drukāt un krāsot kopā var bez konta. Tas, ko tu krāso, paliek tavā ierīcē. Kad krāsojat kopā, otas vilcieni caur mūsu serveri nonāk pie pārējiem istabā, bez vārdiem; ja 30 minūtes neviens nekrāso, istaba tiek slēgta. Vārdi, ko ieraksti dāvanu birkām, nekad netiek sūtīti uz mūsu serveri.</p>
      <p>Lai apmeklētājus neskaitītu divreiz, mēs katru dienu no tavas IP adreses un pārlūka izveidojam kodu, izmantojot atslēgu, kas mainās katru dienu; pašu IP adresi mēs neglabājam. Pēc 90 dienām mēs šo kodu aizstājam ar nejaušu, lai pat mēs vairs nevarētu saistīt uzskaiti ar kādu ierīci. Pašu uzskaiti (kura lapa, kura valsts, telefons vai dators, kad) mēs glabājam, lai redzētu, kā vietne tiek izmantota gadu gaitā.</p>

      <h2>Konts</h2>
      <p>Konti ir paredzēti tikai pieaugušajiem (no 16 gadu vecuma). Bērniem konts nav vajadzīgs, un viņi to nevar izveidot. Ja tev ir konts, mēs glabājam tavu vārdu, e-pasta adresi un izlasi, lai tu to atrastu visās savās ierīcēs. Savu kontu vari izdzēst pašrocīgi; kopā ar to tiek dzēsta arī tava izlase un pieteikšanās e-pasta vēstulēm.</p>

      <h2>E-pasts</h2>
      <p>Ja piesakies e-pasta vēstulēm, mēs glabājam tavu e-pasta adresi, tevis izvēlētās tēmas, kā arī tavu valsti un valodu. Vispirms tu apstiprini pieteikšanos, izmantojot saiti. Mūsu vēstulēs nav izsekošanas pikseļu vai novirzītu saišu, ar kurām mērīt, vai tu tās atver. No vēstulēm vari atteikties ar vienu klikšķi katras vēstules apakšā, un tad mēs izdzēšam tavu adresi.</p>

      <h2>Saziņa</h2>
      <p>Ja tu mums nosūti ziņu, mēs tavu vārdu un e-pasta adresi izmantojam tikai tam, lai tev atbildētu. Ziņu glabājam ne ilgāk kā divpadsmit mēnešus.</p>

      <h2>Pinterest, Facebook un Instagram</h2>
      <p>Kleurhoek publicē savas krāsojamās lapas paša Kleurhoek kontos platformās Pinterest, Facebook un Instagram. Lai to darītu, mēs šos kontus savienojam, izmantojot Pinterest un Meta oficiālo pieteikšanos (OAuth). Šī savienojuma piekļuves pilnvaras mēs glabājam šifrētā veidā un izmantojam tikai tam, lai publicētu ierakstus un izveidotu dēļus savos kontos. Mēs nelasām, nevācam un neglabājam datus par citiem šo pakalpojumu lietotājiem un neizmantojam savienojumu reklāmai. Poga „Saglabāt pakalpojumā Pinterest“ mūsu vietnē ir parasta saite: neviens Pinterest skripts netiek ielādēts. Savienojumu var noņemt jebkurā laikā, un pēc tam mēs izdzēšam piekļuves pilnvaras.</p>

      <h2>Kas mums palīdz</h2>
      <p>Vietne darbojas uzņēmuma Scaleway serveros Amsterdamā. Cloudflare nodrošina ātrumu un drošību, Zitadel – pieteikšanos, bet Brevo sūta mūsu e-pasta vēstules. Tie apstrādā datus tikai mūsu vārdā un tikai šim nolūkam. Ja tu noklikšķini uz saites uz veikalu, piemēram, Amazon, no tā brīža ir spēkā šī veikala privātuma politika.</p>

      <h2>Tavas tiesības</h2>
      <p>Tu vari jautāt, kādus datus par tevi glabājam, un lūgt tos labot vai dzēst. Lai to izdarītu, lūdzu, <Link href={contact("privacy")}>sazinies ar mums</Link>. Ja nepiekrīti tam, kā mēs rīkojamies ar taviem datiem, vari iesniegt sūdzību iestādē Autoriteit Persoonsgegevens (Nīderlandes datu aizsardzības iestāde) vai savas valsts uzraudzības iestādē.</p>

      <h2>Izmaiņas</h2>
      <p>Ja kaut kas mainās attiecībā uz to, ko mēs glabājam, mēs atjauninām šo lapu. Datums augšpusē rāda, kad lapa pēdējoreiz atjaunināta.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Privātuma politika", description: "Kādus datus Kleurhoek glabā, kāpēc un cik ilgi: bez sīkdatnēm, anonīma apmeklējumu uzskaite un konti tikai pieaugušajiem.", Body };
