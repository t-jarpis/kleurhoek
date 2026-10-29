import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het IJslands (ADR 0026), zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Síðast uppfært 24. október 2026.</p>
      <p>Á þessari síðu útskýrum við hvað þú mátt gera við litamyndir og föndurblöð Kleurhoek, hvernig við vísum á aðra vefi og hvernig þú getur látið okkur vita af einhverju. Með því að nota Kleurhoek samþykkir þú þessa skilmála.</p>

      <h2>Okkar eigin hönnun</h2>
      <p>Allar litamyndir, klippiarkir og pappírslíkön á Kleurhoek eru gerð sérstaklega fyrir Kleurhoek. Við búum þau til með hjálp gervigreindar og förum yfir hverja síðu áður en hún fer á netið. Við afritum ekkert af öðrum vefjum eða úr bókum og búum ekki til þekktar persónur, vörumerki eða fígúrur. Vefurinn, nafnið Kleurhoek og myndasafnið tilheyra Kleurhoek.</p>
      <p>Þú mátt nota myndirnar án endurgjalds:</p>
      <ul>
        <li>heima, til að lita, prenta og gefa fjölskyldu og vinum;</li>
        <li>í skólanum, á leikskólanum, í félagi eða á bókasafninu, líka í miklu magni;</li>
        <li>í veislu, til dæmis sem föndur.</li>
      </ul>
      <p>Eftirfarandi er ekki leyfilegt án skriflegs leyfis okkar: að selja myndirnar (stakar, í hefti eða til niðurhals), að setja þær á annan vef, í app eða á samfélagsmiðla sem eigið efni, eða að nota þær í vörur eða auglýsingar. Þér er velkomið að deila tengli á síðuna á Kleurhoek.</p>

      <h2>Þemu frá höfundum</h2>
      <p>Börn leita oft að litamyndum af persónum úr teiknimynd, skemmtigarði eða bók. Þær teikningar tilheyra höfundum sínum og við megum ekki búa þær til eða afrita þær sjálf. En margir höfundar bjóða þær ókeypis á eigin vefsíðum. Undir <Link href={link(base, "/themas")}>Þemu frá höfundum</Link> söfnum við tenglum á þær síður. Um það gildir eftirfarandi:</p>
      <ul>
        <li>Við vísum aðeins á opinberan vef höfundar eða rétthafa, aldrei á vefi sem afrita teikningar annarra.</li>
        <li>Við sýnum hvorki né geymum myndir, teikningar eða merki höfundar. Á okkar vef sérðu aðeins okkar eigin lýsingu og tengil. Þetta getur aðeins verið öðruvísi ef höfundur gefur okkur skriflegt leyfi og þá tökum við það fram.</li>
        <li>Við förum yfir hvern tengil áður en hann fer á netið. Eftir það kannar tölvuforrit á hverjum degi hvort síðan sé enn til. Ef síða hverfur fjarlægjum við tengilinn sjálfkrafa. Við fylgjum alltaf reglum (robots.txt) á vef höfundar.</li>
        <li>Efni á vefjum höfunda er á þeirra eigin ábyrgð og fellur undir þeirra eigin skilmála. Við höfum enga stjórn á því.</li>
      </ul>
      <p>Ert þú höfundur og viltu að við breytum eða fjarlægjum tengil, eða viltu vinna með okkur? <Link href={contact("partnership")}>Hafðu samband</Link>. Við gerum breytinguna innan fimm virkra daga.</p>

      <h2>Vörumerki og nöfn</h2>
      <p>Nöfn persóna, skemmtigarða, þátta og vörumerkja tilheyra eigendum sínum. Við notum þau aðeins til að lýsa því hvar þú finnur eitthvað. Kleurhoek tengist ekki þessum eigendum og er ekki styrkt af þeim, nema það sé sérstaklega tekið fram.</p>

      <h2>Samstarfstenglar</h2>
      <p>Með sumum myndum og þemum nefnum við hluti sem þú getur notað með þeim, til dæmis barnaskæri eða trélitir. Þetta eru samstarfstenglar: ef þú kaupir eitthvað í gegnum slíkan tengil fær Kleurhoek litla þóknun frá versluninni. Þú borgar það sama. Þannig höldum við myndunum ókeypis. Samstarfstenglar eru alltaf greinilega merktir. Verslunin ber ábyrgð á vörunni, verðinu og afhendingunni.</p>

      <h2>Tilkynning um höfundarrétt</h2>
      <p>Telur þú að á Kleurhoek sé eitthvað sem þú átt réttinn að, eða að tengill vísi á eitthvað sem hann ætti ekki að gera? Tilkynntu það í gegnum <Link href={contact("copyright")}>samskiptaformið</Link> með efninu „Höfundarréttur“. Segðu okkur hvaða síðu þetta varðar, hvers vegna þú telur að þetta sé ekki rétt og hvernig við getum náð í þig. Við svörum innan fimm virkra daga og fjarlægjum efnið, ef ástæða er til, á meðan við skoðum málið.</p>

      <h2>Örugg föndurgerð</h2>
      <p>Klippiarkir og pappírslíkön eru ætluð til að búa til með fullorðnum. Notaðu barnaskæri og í lukt skaltu alltaf nota LED-ljós, aldrei alvöru kerti. Smáhlutir henta ekki börnum yngri en þriggja ára.</p>

      <h2>Ábyrgð</h2>
      <p>Við vöndum okkur mikið við Kleurhoek en getum ekki lofað að allt sé alltaf villulaust eða að vefurinn sé alltaf aðgengilegur. Að því marki sem lög leyfa ber Kleurhoek ekki ábyrgð á tjóni sem hlýst af notkun vefsins, myndanna eða vefjanna sem við vísum á.</p>

      <h2>Persónuvernd</h2>
      <p>Við teljum heimsóknir nafnlaust: án vafrakaka, án IP-talna og án nokkurs sem hægt er að rekja til þín. Þú þarft ekki aðgang til að lita eða prenta. Ef þú stofnar aðgang geymum við nafnið þitt, netfangið þitt og eftirlætin þín, svo þú finnir þau í öllum tækjunum þínum; þú getur sjálf(ur) eytt aðganginum hvenær sem er. Ef þú skráir þig fyrir tölvupósti notum við netfangið þitt aðeins til þess og því er eytt þegar þú afskráir þig. Ef þú sendir okkur skilaboð notum við nafnið þitt og netfangið aðeins til að svara þér og geymum skilaboðin í mesta lagi tólf mánuði. Viltu að við eyðum skilaboðunum þínum fyrr? <Link href={contact("privacy")}>Láttu okkur vita</Link>.</p>

      <h2>Breytingar og spurningar</h2>
      <p>Við kunnum að breyta þessum fyrirvara, til dæmis þegar eitthvað nýtt bætist við Kleurhoek. Dagsetningin efst sýnir hvenær hann var síðast uppfærður. Um þennan fyrirvara gilda hollensk lög. Spurningar? <Link href={contact()}>Hafðu samband</Link>.</p>
    </>
  );
}
