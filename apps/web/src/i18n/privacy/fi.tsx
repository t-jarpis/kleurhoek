import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Päivitetty viimeksi 4. marraskuuta 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be ja www.kleurhoek.com) on verkkosivusto, jossa on omia värityskuvia ja askartelupohjia lapsille. Keräämme tietoja mahdollisimman vähän. Tällä sivulla kerrotaan tarkasti, mitä säilytämme, miksi, kuinka kauan ja mitkä ovat oikeutesi.</p>

      <h2>Keitä olemme</h2>
      <p>Kleurhoek on alankomaalainen verkkosivusto. Jos sinulla on kysyttävää tietosuojasta, käytä <Link href={contact("privacy")}>yhteydenottolomakettamme</Link>.</p>

      <h2>Vierailu ja värittäminen</h2>
      <p>Laskemme käynnit nimettömästi: ilman evästeitä, ilman IP-osoitteita ja ilman mitään, mistä sinut voisi tunnistaa. Emme käytä muiden mainos- tai seurantaskriptejä, emme myöskään Googlen, Metan tai Pinterestin. Voit värittää, tulostaa ja värittää yhdessä muiden kanssa ilman tiliä. Värityksesi pysyy omalla laitteellasi. Kun väritätte yhdessä, vedot kulkevat palvelimemme kautta muille huoneessa oleville ilman nimiä; kun kukaan ei ole värittänyt 30 minuuttiin, huone suljetaan. Nimiä, jotka kirjoitat lahjalappuihin, ei koskaan lähetetä palvelimellemme.</p>
      <p>Jotta emme laskisi kävijöitä kahteen kertaan, muodostamme joka päivä koodin IP-osoitteestasi ja selaimestasi avaimella, joka vaihtuu päivittäin; itse IP-osoitetta emme tallenna. 90 päivän kuluttua korvaamme koodin satunnaisella, joten emme enää itsekään voi yhdistää laskentaa laitteeseen. Itse laskentatiedot (mikä sivu, mikä maa, puhelin vai tietokone, milloin) säilytämme, jotta näemme, miten sivustoa käytetään vuosien mittaan.</p>

      <h2>Tili</h2>
      <p>Tilit ovat vain aikuisille (16-vuotiaille ja sitä vanhemmille). Lapset eivät tarvitse tiliä eivätkä voi luoda sellaista. Jos sinulla on tili, säilytämme nimesi, sähköpostiosoitteesi ja suosikkisi, jotta löydät ne kaikilla laitteillasi. Voit poistaa tilisi itse; samalla poistetaan myös suosikkisi ja sähköpostitilauksesi.</p>

      <h2>Sähköposti</h2>
      <p>Jos tilaat sähköpostejamme, säilytämme sähköpostiosoitteesi, valitsemasi aiheet sekä maasi ja kielesi. Vahvistat tilauksen ensin linkin kautta. Sähköposteissamme ei ole seurantapikseleitä eikä uudelleenohjattuja linkkejä, joilla mitattaisiin, avaatko ne. Voit perua tilauksen yhdellä napsautuksella jokaisen sähköpostin lopussa, ja silloin poistamme osoitteesi.</p>

      <h2>Yhteydenotto</h2>
      <p>Jos lähetät meille viestin, käytämme nimeäsi ja sähköpostiosoitettasi vain vastaamiseen. Säilytämme viestin enintään kaksitoista kuukautta.</p>

      <h2>Pinterest, Facebook ja Instagram</h2>
      <p>Kleurhoek julkaisee omia värityskuviaan Kleurhoekin omilla tileillä Pinterestissä, Facebookissa ja Instagramissa. Tätä varten yhdistämme tilit Pinterestin ja Metan virallisen kirjautumisen (OAuth) kautta. Yhteyden käyttöoikeustunnukset säilytämme salattuina ja käytämme niitä vain julkaisujen tekemiseen ja taulujen luomiseen omilla tileillämme. Emme lue, kerää emmekä säilytä tietoja näiden palvelujen muista käyttäjistä, emmekä käytä yhteyttä mainontaan. Sivustomme ”Tallenna Pinterestiin” -painike on tavallinen linkki: Pinterestin skriptiä ei ladata. Yhteys voidaan poistaa milloin tahansa, minkä jälkeen poistamme tunnukset.</p>

      <h2>Ketkä auttavat meitä</h2>
      <p>Sivusto toimii Scalewayn palvelimilla Amsterdamissa. Cloudflare huolehtii nopeudesta ja tietoturvasta, Zitadel kirjautumisesta ja Brevo sähköpostiemme lähettämisestä. Ne käsittelevät tietoja vain puolestamme ja vain tähän tarkoitukseen. Jos napsautat linkkiä kauppaan, kuten Amazoniin, siitä hetkestä alkaen sovelletaan kyseisen kaupan tietosuojakäytäntöä.</p>

      <h2>Oikeutesi</h2>
      <p>Voit kysyä, mitä tietoja meillä on sinusta, ja pyytää korjaamaan tai poistamaan ne. <Link href={contact("privacy")}>Ota yhteyttä</Link> meihin tätä varten. Jos olet eri mieltä siitä, miten käsittelemme tietojasi, voit tehdä valituksen viranomaiselle Autoriteit Persoonsgegevens (Alankomaiden tietosuojaviranomainen) tai oman maasi tietosuojaviranomaiselle.</p>

      <h2>Muutokset</h2>
      <p>Jos säilyttämiimme tietoihin tulee muutoksia, päivitämme tämän sivun. Yläreunan päivämäärä kertoo, milloin sivu on viimeksi päivitetty.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Tietosuojaseloste", description: "Mitä tietoja Kleurhoek säilyttää, miksi ja kuinka kauan: ei evästeitä, nimetön käyntien laskenta ja tilit vain aikuisille.", Body };
