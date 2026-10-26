import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Hongaars (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Utoljára frissítve: 2026. október 24.</p>
      <p>Ezen az oldalon megtudhatod, mit tehetsz a Kleurhoek színezőivel és barkácslapjaival, hogyan linkelünk más weboldalakra, és hogyan jelezhetsz nekünk valamit. A Kleurhoek használatával elfogadod ezeket a feltételeket.</p>

      <h2>Saját terveink</h2>
      <p>A Kleurhoeken található összes színező, kivágós lap és papírmodell kifejezetten a Kleurhoek számára készült. Mesterséges intelligencia segítségével készítjük őket, és minden lapot ellenőrzünk, mielőtt felkerül az oldalra. Semmit nem másolunk más weboldalakról vagy könyvekből, és nem rajzolunk újra ismert szereplőket, márkákat vagy figurákat. A weboldal, a Kleurhoek név és a lapok gyűjteménye a Kleurhoek tulajdona.</p>
      <p>A lapokat ingyen használhatod:</p>
      <ul>
        <li>otthon, színezésre, nyomtatásra, és hogy odaadd a családodnak és a barátaidnak;</li>
        <li>az iskolában, az óvodában, egy egyesületben vagy a könyvtárban, akár nagy számban is;</li>
        <li>egy bulin, például barkácsfoglalkozásként.</li>
      </ul>
      <p>Írásos engedélyünk nélkül nem szabad: a lapokat eladni (egyenként, füzetben vagy letölthető formában), más weboldalon, alkalmazásban vagy a közösségi médiában saját anyagként közzétenni, illetve termékekben vagy reklámban felhasználni. A Kleurhoek oldalára mutató linket nyugodtan megoszthatod.</p>

      <h2>Témák az alkotóktól</h2>
      <p>A gyerekek gyakran keresnek színezőket rajzfilmek, vidámparkok vagy könyvek szereplőiről. Ezek a rajzok az alkotóik tulajdonában vannak, és mi nem készíthetjük el vagy másolhatjuk le őket. Sok alkotó azonban ingyen kínálja őket a saját weboldalán. A <Link href={link(base, "/themas")}>Témák az alkotóktól</Link> részben ezekre az oldalakra mutató linkeket gyűjtünk. Ennek szabályai:</p>
      <ul>
        <li>Csak az alkotó vagy a jogtulajdonos hivatalos weboldalára linkelünk, soha nem olyan oldalakra, amelyek mások rajzait másolják.</li>
        <li>Nem jelenítünk meg és nem tárolunk az alkotótól származó képeket, rajzokat vagy logókat. Az oldalunkon csak a saját leírásunkat és egy linket látsz. Ez csak akkor lehet másként, ha az alkotó írásban engedélyt ad, és ezt ilyenkor jelezzük.</li>
        <li>Minden linket ellenőrzünk, mielőtt felkerül. Ezután egy számítógépes program minden nap megnézi, létezik-e még az oldal. Ha egy oldal eltűnik, a linket automatikusan eltávolítjuk. Ennek során mindig betartjuk az alkotó weboldalának szabályait (robots.txt).</li>
        <li>Az alkotók weboldalainak tartalmáért az alkotók felelnek, és azokra a saját feltételeik vonatkoznak. Nincs beleszólásunk.</li>
      </ul>
      <p>Alkotó vagy, és szeretnéd, hogy módosítsunk vagy töröljünk egy linket, esetleg együttműködnél velünk? <Link href={contact("partnership")}>Vedd fel velünk a kapcsolatot</Link>. A módosítást öt munkanapon belül elvégezzük.</p>

      <h2>Márkák és nevek</h2>
      <p>A szereplők, vidámparkok, sorozatok és márkák nevei a tulajdonosaikéi. Csak arra használjuk őket, hogy leírjuk, hol találsz meg valamit. A Kleurhoek nem áll kapcsolatban ezekkel a tulajdonosokkal, és nem ők szponzorálják, kivéve, ha ezt kifejezetten jelezzük.</p>

      <h2>Partnerlinkek</h2>
      <p>Néhány lapnál és témánál megemlítünk olyan dolgokat, amelyeket hozzájuk használhatsz, például gyerekollót vagy színes ceruzát. Ezek partnerlinkek: ha egy ilyen linken keresztül vásárolsz valamit, a Kleurhoek kis jutalékot kap a bolttól. Te ugyanannyit fizetsz. Így maradhatnak ingyenesek a lapok. A partnerlinkeket mindig egyértelműen jelöljük. A termékért, az árért és a szállításért a bolt felel.</p>

      <h2>Szerzői jogi bejelentés</h2>
      <p>Úgy gondolod, hogy a Kleurhoeken van valami, amihez neked vannak jogaid, vagy hogy egy link olyan helyre mutat, ahová nem kellene? Jelezd a <Link href={contact("copyright")}>kapcsolatfelvételi űrlapon</Link> &quot;Szerzői jog&quot; tárggyal. Írd meg, melyik oldalról van szó, miért gondolod, hogy nincs rendben, és hogyan érhetünk el. Öt munkanapon belül válaszolunk, és ha okunk van rá, a vizsgálat idejére eltávolítjuk.</p>

      <h2>Biztonságos barkácsolás</h2>
      <p>A kivágós lapokat és papírmodelleket felnőttel együtt érdemes elkészíteni. Használj gyerekollót, a lámpásokba pedig mindig LED-es fényt tegyél, soha ne igazi gyertyát. Az apró részek három év alatti gyerekeknek nem valók.</p>

      <h2>Felelősség</h2>
      <p>A Kleurhoeket nagy gondossággal készítjük, de nem ígérhetjük, hogy minden mindig hibátlan, vagy hogy a weboldal mindig elérhető. A jogszabályok által megengedett mértékben a Kleurhoek nem felel a weboldal, a lapok vagy az általunk linkelt weboldalak használatából eredő károkért.</p>

      <h2>Adatvédelem</h2>
      <p>A látogatásokat névtelenül számoljuk: sütik nélkül, IP-címek nélkül, és semmi olyan nélkül, ami visszavezethető hozzád. A színezéshez és a nyomtatáshoz nem kell fiók. Ha mégis létrehozol egyet, megőrizzük a nevedet, az e-mail-címedet és a kedvenceidet, hogy minden eszközödön megtaláld őket; a fiókodat bármikor magad törölheted. Ha feliratkozol e-mailekre, a címedet csak erre használjuk, és a leiratkozással töröljük. Ha üzenetet küldesz nekünk, a nevedet és az e-mail-címedet csak a válaszhoz használjuk, az üzenetet pedig legfeljebb tizenkét hónapig őrizzük meg. Szeretnéd, hogy hamarabb töröljük az üzenetedet? <Link href={contact("privacy")}>Szólj nekünk</Link>.</p>

      <h2>Változások és kérdések</h2>
      <p>Ezt a nyilatkozatot módosíthatjuk, például ha valami új kerül a Kleurhoekre. A fenti dátum mutatja, mikor frissült utoljára. Erre a nyilatkozatra a holland jog az irányadó. Kérdésed van? <Link href={contact()}>Vedd fel velünk a kapcsolatot</Link>.</p>
    </>
  );
}
