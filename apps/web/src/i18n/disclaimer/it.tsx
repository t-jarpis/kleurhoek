import Link from "next/link";
import { link } from "@/lib/sites";
import type { DisclaimerProps } from "./types";

/** Disclaimer in het Italiaans (ADR 0026). Zelfde opbouw als nl.tsx. */
export function Disclaimer({ base, contact }: DisclaimerProps) {
  return (
    <>
      <p className="kh-meta">Ultimo aggiornamento: 24 ottobre 2026.</p>
      <p>In questa pagina trovi cosa puoi fare con i disegni da colorare e i lavoretti di Kleurhoek, come mettiamo i link ad altri siti web e come puoi segnalarci qualcosa. Usando Kleurhoek accetti queste regole.</p>

      <h2>Disegni nostri</h2>
      <p>Tutti i disegni da colorare, da ritagliare e da costruire su Kleurhoek sono creati apposta per Kleurhoek. Li realizziamo con l&apos;aiuto dell&apos;IA e controlliamo ogni disegno prima di pubblicarlo. Non copiamo nulla da altri siti web o da libri e non riproduciamo personaggi, marchi o figure famose. Il sito, il nome Kleurhoek e la raccolta di disegni appartengono a Kleurhoek.</p>
      <p>Puoi usare i disegni gratis:</p>
      <ul>
        <li>a casa, per colorarli, stamparli e regalarli a parenti e amici;</li>
        <li>a scuola, all&apos;asilo, in un&apos;associazione o in biblioteca, anche in grandi quantità;</li>
        <li>a una festa, per esempio come attività creativa.</li>
      </ul>
      <p>Senza il nostro permesso scritto non è consentito: vendere i disegni (singoli, in un libretto o come download), pubblicarli come materiale proprio su un altro sito web, in un&apos;app o sui social media, oppure usarli in prodotti o pubblicità. Puoi invece condividerli con un link al disegno su Kleurhoek.</p>

      <h2>Temi dagli autori</h2>
      <p>I bambini cercano spesso disegni da colorare di personaggi di un cartone animato, di un parco divertimenti o di un libro. Quei disegni appartengono ai loro autori e noi non possiamo crearli né copiarli. Però molti autori li offrono gratis sul proprio sito web. Nella sezione <Link href={link(base, "/themas")}>Temi dagli autori</Link> raccogliamo i link a quelle pagine. Valgono queste regole:</p>
      <ul>
        <li>Mettiamo link solo al sito ufficiale dell&apos;autore o del titolare dei diritti, mai a siti che riprendono disegni di altri.</li>
        <li>Non mostriamo immagini, disegni o loghi dell&apos;autore e non li salviamo. Da noi vedi solo una nostra descrizione e un link. Può essere diverso solo se un autore ci dà il suo permesso scritto; in quel caso lo indichiamo.</li>
        <li>Controlliamo ogni link prima che venga pubblicato. Poi un programma verifica ogni giorno che la pagina esista ancora. Se una pagina sparisce, togliamo il link automaticamente. Rispettiamo sempre le regole (robots.txt) del sito web dell&apos;autore.</li>
        <li>Il contenuto dei siti web degli autori è sotto la loro responsabilità e segue le loro condizioni. Noi non abbiamo alcun controllo su di esso.</li>
      </ul>
      <p>Sei un autore e vuoi che modifichiamo o togliamo un link, oppure vuoi collaborare con noi? <Link href={contact("partnership")}>Contattaci</Link>. Faremo la modifica entro cinque giorni lavorativi.</p>

      <h2>Marchi e nomi</h2>
      <p>I nomi di personaggi, parchi divertimenti, serie e marchi appartengono ai loro proprietari. Li usiamo solo per descrivere dove puoi trovare qualcosa. Kleurhoek non è collegato a questi proprietari e non è sponsorizzato da loro, salvo quando è indicato espressamente.</p>

      <h2>Link partner</h2>
      <p>Per alcuni disegni e temi suggeriamo del materiale da usare, come delle forbici per bambini o delle matite colorate. Sono link partner: se compri qualcosa tramite uno di questi link, il negozio dà a Kleurhoek un piccolo compenso. Tu paghi lo stesso prezzo. Così i disegni restano gratis. I link partner sono sempre indicati chiaramente. Il negozio è responsabile del prodotto, del prezzo e della consegna.</p>

      <h2>Segnalare una violazione del diritto d&apos;autore</h2>
      <p>Pensi che su Kleurhoek ci sia qualcosa su cui hai dei diritti, o che un link porti a qualcosa che non dovrebbe esserci? Segnalacelo tramite il <Link href={contact("copyright")}>modulo di contatto</Link> scegliendo come argomento &quot;Diritto d&apos;autore&quot;. Indica di quale pagina si tratta, perché secondo te non va bene e come possiamo contattarti. Rispondiamo entro cinque giorni lavorativi e, se c&apos;è motivo, togliamo il contenuto mentre verifichiamo.</p>

      <h2>Lavoretti in sicurezza</h2>
      <p>I disegni da ritagliare e da costruire sono pensati per essere fatti insieme a un adulto. Usa delle forbici per bambini e, per le lanterne, sempre una lucina a LED e mai una candela vera. Le parti piccole non sono adatte ai bambini sotto i tre anni.</p>

      <h2>Responsabilità</h2>
      <p>Realizziamo Kleurhoek con molta cura, ma non possiamo garantire che tutto sia sempre privo di errori o che il sito web sia sempre raggiungibile. Nei limiti consentiti dalla legge, Kleurhoek non è responsabile per danni derivanti dall&apos;uso del sito web, dei disegni o dei siti web a cui rimandiamo.</p>

      <h2>Privacy</h2>
      <p>Contiamo le visite in modo anonimo: senza cookie, senza indirizzo IP e senza nulla che possa ricondurre a te. Per colorare o stampare non serve un account. Se ne crei uno, conserviamo il tuo nome, il tuo indirizzo e-mail e i tuoi preferiti, così li ritrovi su tutti i tuoi dispositivi; puoi eliminare il tuo account in qualsiasi momento. Se ti iscrivi alle email, usiamo il tuo indirizzo solo per quello, e disiscriverti lo cancella. Se ci invii un messaggio, usiamo il tuo nome e il tuo indirizzo e-mail solo per risponderti e conserviamo il messaggio al massimo dodici mesi. Vuoi che cancelliamo il tuo messaggio prima? <Link href={contact("privacy")}>Faccelo sapere</Link>.</p>

      <h2>Modifiche e domande</h2>
      <p>Possiamo modificare queste note legali, per esempio quando su Kleurhoek arriva qualcosa di nuovo. In alto trovi la data dell&apos;ultimo aggiornamento. Queste note legali sono regolate dalla legge olandese. Domande? <Link href={contact()}>Contattaci</Link>.</p>
    </>
  );
}
