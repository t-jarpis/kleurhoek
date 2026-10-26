import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in Finnish (ADR 0026). Same structure as nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Päivitetty viimeksi 24. lokakuuta 2026.</p>
      <p>Tällä sivulla kerrotaan, mitä saat tehdä Kleurhoekin värityskuvilla ja askartelusivuilla, miten linkitämme muille verkkosivustoille ja miten voit ilmoittaa meille jostakin. Käyttämällä Kleurhoekia hyväksyt nämä ehdot.</p>

      <h2>Omat kuvamme</h2>
      <p>Kaikki Kleurhoekin värityskuvat, leikkuuarkit ja paperimallit on tehty erityisesti Kleurhoekia varten. Teemme ne tekoälyn avulla ja tarkistamme jokaisen kuvan ennen kuin se julkaistaan. Emme kopioi mitään muilta verkkosivustoilta tai kirjoista, emmekä jäljittele tunnettuja hahmoja, tavaramerkkejä tai henkilöitä. Verkkosivusto, Kleurhoek-nimi ja kuvakokoelma kuuluvat Kleurhoekille.</p>
      <p>Saat käyttää kuvia maksutta:</p>
      <ul>
        <li>kotona värittämiseen, tulostamiseen ja jakamiseen perheelle ja ystäville;</li>
        <li>koulussa, päiväkodissa, kerhossa tai kirjastossa, myös suurina määrinä;</li>
        <li>juhlissa, esimerkiksi askartelutekemisenä.</li>
      </ul>
      <p>Seuraava ei ole sallittua ilman kirjallista lupaamme: kuvien myyminen (yksittäin, vihkona tai ladattavana tiedostona), niiden julkaiseminen toisella verkkosivustolla, sovelluksessa tai sosiaalisessa mediassa omana materiaalinasi tai niiden käyttäminen tuotteissa tai mainonnassa. Saat mielellään jakaa linkin Kleurhoekin sivulle.</p>

      <h2>Teemat tekijöiltä</h2>
      <p>Lapset etsivät usein värityskuvia piirrossarjojen, huvipuistojen tai kirjojen hahmoista. Nämä piirrokset kuuluvat tekijöilleen, emmekä saa itse tehdä tai kopioida niitä. Monet tekijät tarjoavat niitä kuitenkin ilmaiseksi omilla verkkosivustoillaan. Osioon <Link href={link(base, "/themas")}>Teemat tekijöiltä</Link> keräämme linkkejä näille sivuille. Seuraavat periaatteet ovat voimassa:</p>
      <ul>
        <li>Linkitämme vain tekijän tai oikeudenhaltijan viralliselle verkkosivustolle, emme koskaan sivustoille, jotka kopioivat muiden piirroksia.</li>
        <li>Emme näytä tai tallenna tekijän kuvia, piirroksia tai logoja. Sivustollamme näet vain oman kuvauksemme ja linkin. Tämä voi poiketa vain, jos tekijä antaa meille kirjallisen luvan, ja silloin kerromme siitä.</li>
        <li>Tarkistamme jokaisen linkin ennen sen julkaisemista. Sen jälkeen tietokoneohjelma tarkistaa päivittäin, onko sivu yhä olemassa. Jos sivu katoaa, poistamme linkin automaattisesti. Noudatamme aina tekijän verkkosivuston sääntöjä (robots.txt).</li>
        <li>Tekijöiden verkkosivustojen sisältö on heidän omalla vastuullaan, ja siihen sovelletaan heidän omia ehtojaan. Emme voi vaikuttaa siihen.</li>
      </ul>
      <p>Oletko tekijä ja haluatko, että muutamme tai poistamme linkin, tai haluatko tehdä kanssamme yhteistyötä? <Link href={contact("partnership")}>Ota meihin yhteyttä</Link>. Teemme muutoksen viiden arkipäivän kuluessa.</p>

      <h2>Tavaramerkit ja nimet</h2>
      <p>Hahmojen, huvipuistojen, sarjojen ja tavaramerkkien nimet kuuluvat omistajilleen. Käytämme niitä vain kertoaksemme, mistä jotain löytyy. Kleurhoek ei ole sidoksissa näihin omistajiin eivätkä he sponsoroi sitä, ellei toisin ole nimenomaisesti mainittu.</p>

      <h2>Kumppanilinkit</h2>
      <p>Joidenkin kuvien ja teemojen yhteydessä mainitsemme tarvikkeita, joita voit käyttää niiden kanssa, esimerkiksi lasten saksia tai värikyniä. Nämä ovat kumppanilinkkejä: jos ostat jotain tällaisen linkin kautta, Kleurhoek saa kaupalta pienen palkkion. Sinä maksat saman verran. Näin pidämme kuvat ilmaisina. Kumppanilinkit on aina merkitty selvästi. Kauppa vastaa tuotteesta, hinnasta ja toimituksesta.</p>

      <h2>Tekijänoikeusilmoitus</h2>
      <p>Onko Kleurhoekissa mielestäsi jotain, johon sinulla on oikeudet, tai johtaako linkki johonkin, mihin sen ei pitäisi? Ilmoita siitä <Link href={contact("copyright")}>yhteydenottolomakkeella</Link> aiheella &quot;Tekijänoikeus&quot;. Kerro, mitä sivua asia koskee, miksi asia ei mielestäsi ole kunnossa ja miten tavoitamme sinut. Vastaamme viiden arkipäivän kuluessa ja poistamme sisällön tarvittaessa selvityksen ajaksi.</p>

      <h2>Turvallista askartelua</h2>
      <p>Leikkuuarkit ja paperimallit on tarkoitettu tehtäviksi yhdessä aikuisen kanssa. Käytä lasten saksia ja käytä lyhdyissä aina LED-valoa, ei koskaan oikeaa kynttilää. Pienet osat eivät sovi alle kolmevuotiaille.</p>

      <h2>Vastuu</h2>
      <p>Teemme Kleurhoekia huolellisesti, mutta emme voi luvata, että kaikki on aina virheetöntä tai että sivusto on aina käytettävissä. Lain sallimissa rajoissa Kleurhoek ei vastaa vahingoista, jotka johtuvat sivuston, kuvien tai linkittämiemme sivustojen käytöstä.</p>

      <h2>Tietosuoja</h2>
      <p>Laskemme käynnit nimettömästi: ilman evästeitä, ilman IP-osoitteita ja ilman mitään, mikä voitaisiin yhdistää sinuun. Et tarvitse tiliä värittämiseen tai tulostamiseen. Jos kuitenkin luot tilin, tallennamme nimesi, sähköpostiosoitteesi ja suosikkisi, jotta löydät ne kaikilta laitteiltasi; voit poistaa tilisi itse milloin tahansa. Jos tilaat sähköposteja, käytämme osoitettasi vain siihen, ja tilauksen peruminen poistaa sen. Jos lähetät meille viestin, käytämme nimeäsi ja sähköpostiosoitettasi vain vastataksemme sinulle, ja säilytämme viestiä enintään kaksitoista kuukautta. Haluatko, että poistamme viestisi aiemmin? <Link href={contact("privacy")}>Kerro meille</Link>.</p>

      <h2>Muutokset ja kysymykset</h2>
      <p>Voimme muuttaa tätä vastuuvapauslauseketta esimerkiksi silloin, kun Kleurhoekiin tulee jotain uutta. Yläreunan päivämäärä kertoo, milloin se on viimeksi päivitetty. Tähän vastuuvapauslausekkeeseen sovelletaan Alankomaiden lakia. Kysyttävää? <Link href={contact()}>Ota meihin yhteyttä</Link>.</p>
    </>
  );
}
