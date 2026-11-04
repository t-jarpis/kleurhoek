import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Síðast uppfært 4. nóvember 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be og www.kleurhoek.com) er vefsíða með frumsömdum litamyndum og föndurblöðum fyrir börn. Við söfnum eins litlu og hægt er. Á þessari síðu kemur nákvæmlega fram hvað við geymum þó, hvers vegna, hve lengi og hver réttindi þín eru.</p>

      <h2>Hver við erum</h2>
      <p>Kleurhoek er hollensk vefsíða. Ef þú hefur spurningar um persónuvernd skaltu nota <Link href={contact("privacy")}>samskiptaeyðublaðið</Link> okkar.</p>

      <h2>Heimsóknir og litun</h2>
      <p>Við teljum heimsóknir nafnlaust: án vafrakaka, án IP-talna og án nokkurs sem hægt er að rekja til þín. Við notum engar auglýsinga- eða rakningarforskriftir frá öðrum, ekki heldur frá Google, Meta eða Pinterest. Þú getur litað, prentað og litað með öðrum án aðgangs. Það sem þú litar verður eftir í þínu eigin tæki. Þegar þið litið saman fara strokurnar í gegnum netþjóninn okkar til hinna í herberginu, án nafna; ef enginn litar í 30 mínútur lokast herbergið. Nöfn sem þú slærð inn á gjafamiða eru aldrei send á netþjóninn okkar.</p>
      <p>Til að telja gesti ekki tvisvar búum við til kóða á hverjum degi út frá IP-tölunni þinni og vafranum, með lykli sem breytist daglega; IP-töluna sjálfa geymum við ekki. Eftir 90 daga skiptum við þeim kóða út fyrir handahófskenndan kóða, svo að ekki einu sinni við getum lengur tengt talningu við tæki. Talningarnar sjálfar (hvaða síða, hvaða land, sími eða tölva, hvenær) geymum við, svo að við sjáum hvernig síðan er notuð í gegnum árin.</p>

      <h2>Aðgangur</h2>
      <p>Aðgangar eru aðeins fyrir fullorðna (16 ára og eldri). Börn þurfa ekki aðgang og geta ekki stofnað hann. Ef þú ert með aðgang geymum við nafnið þitt, netfangið þitt og eftirlætin þín, svo þú finnir þau í öllum tækjunum þínum. Þú getur eytt aðganginum þínum á eigin spýtur; eftirlætin þín og skráningin á póstlistann eyðast þá líka.</p>

      <h2>Tölvupóstur</h2>
      <p>Ef þú skráir þig fyrir tölvupósti geymum við netfangið þitt, efnin sem þú velur og landið þitt og tungumál. Þú staðfestir fyrst skráninguna með tengli. Í tölvupóstunum okkar eru engir rakningarpixlar eða framsendir tenglar til að mæla hvort þú opnir þá. Þú getur afskráð þig með einum smelli neðst í hverjum pósti og þá eyðum við netfanginu þínu.</p>

      <h2>Samband</h2>
      <p>Ef þú sendir okkur skilaboð notum við nafnið þitt og netfangið eingöngu til að svara þér. Við geymum skilaboðin í mesta lagi í tólf mánuði.</p>

      <h2>Pinterest, Facebook og Instagram</h2>
      <p>Kleurhoek birtir eigin litamyndir á eigin reikningum Kleurhoek á Pinterest, Facebook og Instagram. Til þess tengjum við þessa reikninga í gegnum opinbera innskráningu (OAuth) Pinterest og Meta. Aðgangslyklana fyrir þessa tengingu geymum við dulkóðaða og notum þá eingöngu til að birta færslur og búa til töflur á okkar eigin reikningum. Við lesum hvorki, söfnum né geymum gögn um aðra notendur þessara miðla og notum tenginguna ekki fyrir auglýsingar. Hnappurinn „Vista á Pinterest“ á síðunni okkar er venjulegur tengill: engin forskrift frá Pinterest er hlaðin. Hægt er að fjarlægja tenginguna hvenær sem er og eftir það eyðum við aðgangslyklunum.</p>

      <h2>Hverjir hjálpa okkur</h2>
      <p>Vefsíðan keyrir hjá Scaleway í Amsterdam. Cloudflare sér um hraða og öryggi, Zitadel um innskráningu og Brevo sendir tölvupóstinn okkar. Þau vinna gögn eingöngu fyrir okkar hönd og eingöngu í þeim tilgangi. Ef þú smellir á tengil á verslun, eins og Amazon, gildir persónuverndarstefna þeirrar verslunar frá þeirri stundu.</p>

      <h2>Réttindi þín</h2>
      <p>Þú mátt spyrja hvaða gögn við höfum um þig og láta leiðrétta þau eða eyða þeim. <Link href={contact("privacy")}>Hafðu samband</Link> við okkur til þess. Ef þú ert ekki sammála því hvernig við förum með gögnin þín getur þú lagt fram kvörtun hjá Autoriteit Persoonsgegevens (hollensku persónuverndarstofnuninni) eða eftirlitsstofnuninni í þínu landi.</p>

      <h2>Breytingar</h2>
      <p>Ef eitthvað breytist í því sem við geymum uppfærum við þessa síðu. Dagsetningin efst sýnir hvenær hún var síðast uppfærð.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Persónuverndarstefna", description: "Hvaða gögn Kleurhoek geymir, hvers vegna og hve lengi: engar vafrakökur, nafnlaus talning heimsókna og aðgangar aðeins fyrir fullorðna.", Body };
