import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Viimati uuendatud 4. novembril 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be ja www.kleurhoek.com) on veebisait, kus on lastele omaloomingulised värvimispildid ja meisterdamislehed. Kogume võimalikult vähe andmeid. Sellel lehel on täpselt kirjas, mida me siiski säilitame, miks, kui kaua ja millised on sinu õigused.</p>

      <h2>Kes me oleme</h2>
      <p>Kleurhoek on Hollandi veebisait. Privaatsusküsimuste korral kasuta palun meie <Link href={contact("privacy")}>kontaktivormi</Link>.</p>

      <h2>Külastamine ja värvimine</h2>
      <p>Loendame külastusi anonüümselt: ilma küpsisteta, ilma IP-aadressideta ja ilma millegita, mida saaks sinuni tagasi viia. Me ei kasuta kellegi teise reklaami- ega jälgimisskripte, ka mitte Google&apos;i, Meta ega Pinteresti omi. Värvida, printida ja koos värvida saab ilma kontota. See, mida värvid, jääb sinu enda seadmesse. Kui värvite koos, liiguvad pintslitõmbed meie serveri kaudu teistele samas toas olijatele, ilma nimedeta; kui 30 minuti jooksul keegi ei värvi, tuba suletakse. Nimesid, mida kingisiltide jaoks sisestad, ei saadeta kunagi meie serverisse.</p>
      <p>Et külastajaid topelt mitte loendada, loome sinu IP-aadressist ja brauserist iga päev koodi võtmega, mis vahetub iga päev; IP-aadressi ennast me ei salvesta. 90 päeva pärast asendame selle koodi juhusliku koodiga, nii et isegi meie ei saa loendust enam ühegi seadmega siduda. Loendused ise (milline leht, milline riik, telefon või arvuti, millal) säilitame, et näha, kuidas saiti aastate jooksul kasutatakse.</p>

      <h2>Konto</h2>
      <p>Kontod on ainult täiskasvanutele (16-aastastele ja vanematele). Lapsed ei vaja kontot ega saa seda luua. Kui sul on konto, säilitame sinu nime, e-posti aadressi ja lemmikud, et leiaksid need kõigis oma seadmetes. Saad oma konto ise kustutada; koos sellega kustutatakse ka sinu lemmikud ja e-kirjade tellimus.</p>

      <h2>E-kirjad</h2>
      <p>Kui tellid e-kirjad, säilitame sinu e-posti aadressi, valitud teemad ning sinu riigi ja keele. Kõigepealt kinnitad tellimuse lingi kaudu. Meie e-kirjades pole jälgimispiksleid ega ümbersuunatud linke, millega mõõta, kas sa neid avad. Tellimusest saad loobuda ühe klõpsuga iga e-kirja allosas ja siis kustutame sinu aadressi.</p>

      <h2>Kontakt</h2>
      <p>Kui saadad meile sõnumi, kasutame sinu nime ja e-posti aadressi ainult sulle vastamiseks. Säilitame sõnumit kõige rohkem kaksteist kuud.</p>

      <h2>Pinterest, Facebook ja Instagram</h2>
      <p>Kleurhoek avaldab oma värvimispilte Kleurhoeki enda kontodel Pinterestis, Facebookis ja Instagramis. Selleks ühendame need kontod Pinteresti ja Meta ametliku sisselogimise (OAuth) kaudu. Selle ühenduse juurdepääsulubasid hoiame krüpteeritult ja kasutame neid ainult postituste avaldamiseks ja tahvlite loomiseks oma kontodel. Me ei loe, kogu ega säilita nende teenuste teiste kasutajate andmeid ega kasuta ühendust reklaamiks. Nupp „Salvesta Pinterestisse“ meie saidil on tavaline link: ühtegi Pinteresti skripti ei laadita. Ühenduse saab igal ajal eemaldada, misjärel kustutame juurdepääsuload.</p>

      <h2>Kes meid aitavad</h2>
      <p>Veebisait töötab Scaleway serverites Amsterdamis. Cloudflare tagab kiiruse ja turvalisuse, Zitadel haldab sisselogimist ja Brevo saadab meie e-kirju. Nad töötlevad andmeid ainult meie nimel ja ainult selleks otstarbeks. Kui klõpsad poe lingil, näiteks Amazoni lingil, kehtib sellest hetkest selle poe privaatsuspoliitika.</p>

      <h2>Sinu õigused</h2>
      <p>Võid küsida, milliseid andmeid me sinu kohta säilitame, ning lasta neid parandada või kustutada. Selleks <Link href={contact("privacy")}>võta meiega ühendust</Link>. Kui sa ei ole nõus sellega, kuidas me sinu andmeid käitleme, võid esitada kaebuse asutusele Autoriteit Persoonsgegevens (Hollandi andmekaitseasutus) või oma riigi järelevalveasutusele.</p>

      <h2>Muudatused</h2>
      <p>Kui midagi muutub selles, mida me säilitame, uuendame seda lehte. Ülal olev kuupäev näitab, millal lehte viimati uuendati.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Privaatsuspoliitika", description: "Milliseid andmeid Kleurhoek säilitab, miks ja kui kaua: küpsiseid pole, külastusi loetakse anonüümselt ja kontod on ainult täiskasvanutele.", Body };
