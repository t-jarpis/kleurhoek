import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Latvian (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Pēdējo reizi atjaunināts 2026. gada 24. oktobrī.</p>
      <p>Šajā lapā paskaidrots, ko drīkst darīt ar Kleurhoek krāsojamajām lapām un rokdarbu lapām, kā mēs norādām saites uz citām tīmekļa vietnēm un kā mums par kaut ko ziņot. Izmantojot Kleurhoek, tu piekrīti šiem noteikumiem.</p>

      <h2>Mūsu pašu dizains</h2>
      <p>Visas Kleurhoek krāsojamās lapas, izgriežamās lapas un papīra modeļi ir veidoti īpaši Kleurhoek. Mēs tos veidojam ar mākslīgā intelekta palīdzību un pirms publicēšanas pārbaudām katru lapu. Mēs neko nekopējam no citām tīmekļa vietnēm vai grāmatām un neatveidojam zināmus tēlus, zīmolus vai figūras. Tīmekļa vietne, nosaukums Kleurhoek un lapu kolekcija pieder Kleurhoek.</p>
      <p>Lapas vari izmantot bez maksas:</p>
      <ul>
        <li>mājās, lai tās izkrāsotu, izdrukātu un iedotu ģimenei un draugiem;</li>
        <li>skolā, bērnudārzā, pulciņā vai bibliotēkā, arī lielā skaitā;</li>
        <li>svētkos, piemēram, kā radošo nodarbību.</li>
      </ul>
      <p>Bez mūsu rakstiskas atļaujas nav atļauts: pārdot lapas (atsevišķi, grāmatiņā vai kā lejupielādi), ievietot tās citā tīmekļa vietnē, lietotnē vai sociālajos tīklos kā savu materiālu vai izmantot tās produktos vai reklāmā. Dalīties ar saiti uz lapu Kleurhoek vietnē vari vienmēr.</p>

      <h2>Tēmas no veidotājiem</h2>
      <p>Bērni bieži meklē krāsojamās lapas ar tēliem no multfilmām, atrakciju parkiem vai grāmatām. Šie zīmējumi pieder to veidotājiem, un mums nav atļauts tos pašiem veidot vai kopēt. Taču daudzi veidotāji tos bez maksas piedāvā savās tīmekļa vietnēs. Sadaļā <Link href={link(base, "/themas")}>Tēmas no veidotājiem</Link> mēs apkopojam saites uz šīm lapām. Spēkā ir šādi noteikumi:</p>
      <ul>
        <li>Mēs norādām saites tikai uz veidotāja vai tiesību īpašnieka oficiālo tīmekļa vietni, nekad uz vietnēm, kas kopē citu zīmējumus.</li>
        <li>Mēs nerādām un neglabājam veidotāja attēlus, zīmējumus vai logotipus. Mūsu vietnē tu redzi tikai mūsu pašu aprakstu un saiti. Izņēmums iespējams tikai tad, ja veidotājs mums dod rakstisku atļauju, un tādā gadījumā mēs to norādām.</li>
        <li>Pirms publicēšanas mēs pārbaudām katru saiti. Pēc tam datorprogramma katru dienu pārbauda, vai lapa joprojām pastāv. Ja lapa pazūd, mēs saiti automātiski noņemam. To darot, mēs vienmēr ievērojam veidotāja vietnes noteikumus (robots.txt).</li>
        <li>Par veidotāju tīmekļa vietņu saturu atbild paši veidotāji, un uz to attiecas viņu pašu noteikumi. Mēs to nekontrolējam.</li>
      </ul>
      <p>Esi veidotājs un vēlies, lai mēs kādu saiti mainām vai noņemam, vai vēlies ar mums sadarboties? <Link href={contact("partnership")}>Sazinies ar mums</Link>. Izmaiņas veiksim piecu darba dienu laikā.</p>

      <h2>Zīmoli un nosaukumi</h2>
      <p>Tēlu, atrakciju parku, seriālu un zīmolu nosaukumi pieder to īpašniekiem. Mēs tos izmantojam tikai, lai aprakstītu, kur kaut ko var atrast. Kleurhoek nav saistīts ar šiem īpašniekiem un nesaņem no viņiem sponsorēšanu, ja vien tas nav skaidri norādīts.</p>

      <h2>Partneru saites</h2>
      <p>Pie dažām lapām un tēmām mēs pieminam lietas, ko var izmantot kopā ar tām, piemēram, bērnu šķēres vai krāsainos zīmuļus. Tās ir partneru saites: ja tu kaut ko nopērc, izmantojot šādu saiti, Kleurhoek no veikala saņem nelielu atlīdzību. Tu maksā tikpat. Tā lapas paliek bezmaksas. Partneru saites vienmēr ir skaidri atzīmētas. Par produktu, cenu un piegādi atbild veikals.</p>

      <h2>Ziņošana par autortiesībām</h2>
      <p>Tev šķiet, ka Kleurhoek vietnē ir kaut kas, uz ko tev pieder tiesības, vai ka kāda saite ved uz to, uz ko tai nevajadzētu vest? Ziņo par to, izmantojot <Link href={contact("copyright")}>saziņas veidlapu</Link> ar tēmu &quot;Autortiesības&quot;. Norādi, par kuru lapu ir runa, kāpēc tev šķiet, ka kaut kas nav pareizi, un kā ar tevi sazināties. Mēs atbildēsim piecu darba dienu laikā un, ja būs pamats, to noņemsim, kamēr lietu izskatām.</p>

      <h2>Droši rokdarbi</h2>
      <p>Izgriežamās lapas un papīra modeļi ir paredzēti darināšanai kopā ar pieaugušo. Izmanto bērnu šķēres, un lukturīšos vienmēr lieto LED gaismu, nekad īstu sveci. Sīkas detaļas nav piemērotas bērniem līdz trīs gadu vecumam.</p>

      <h2>Atbildība</h2>
      <p>Mēs veidojam Kleurhoek ļoti rūpīgi, taču nevaram apsolīt, ka viss vienmēr būs bez kļūdām vai ka vietne vienmēr būs pieejama. Ciktāl to pieļauj likums, Kleurhoek neatbild par zaudējumiem, kas radušies, izmantojot vietni, lapas vai tīmekļa vietnes, uz kurām mēs norādām saites.</p>

      <h2>Privātums</h2>
      <p>Apmeklējumus mēs skaitām anonīmi: bez sīkdatnēm, bez IP adresēm un bez nekā, ko varētu saistīt ar tevi. Lai krāsotu vai drukātu, konts nav vajadzīgs. Ja tomēr to izveido, mēs glabājam tavu vārdu, e-pasta adresi un izlasi, lai tu tās atrastu visās savās ierīcēs; kontu vari jebkurā laikā izdzēst pats. Ja piesakies e-pastiem, tavu adresi izmantojam tikai tam, un atsakoties tā tiek dzēsta. Ja tu mums nosūti ziņu, tavu vārdu un e-pasta adresi izmantojam tikai, lai tev atbildētu, un ziņu glabājam ne ilgāk kā divpadsmit mēnešus. Vēlies, lai tavu ziņu izdzēšam ātrāk? <Link href={contact("privacy")}>Pastāsti mums</Link>.</p>

      <h2>Izmaiņas un jautājumi</h2>
      <p>Mēs varam šo atrunu mainīt, piemēram, kad Kleurhoek parādās kaut kas jauns. Datums augšā rāda, kad tā pēdējo reizi atjaunināta. Uz šo atrunu attiecas Nīderlandes tiesības. Jautājumi? <Link href={contact()}>Sazinies ar mums</Link>.</p>
    </>
  );
}
