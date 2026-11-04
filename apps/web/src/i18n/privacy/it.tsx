import Link from "next/link";
import type { PrivacyProps, PrivacyText } from "./types";

function Body({ contact }: PrivacyProps) {
  return (
    <>
      <p className="kh-meta">Ultimo aggiornamento: 4 novembre 2026.</p>
      <p>Kleurhoek (www.kleurhoek.nl, www.kleurhoek.be e www.kleurhoek.com) è un sito con disegni da colorare e schede di lavoretti originali per bambini. Raccogliamo il meno possibile. In questa pagina spieghiamo esattamente cosa conserviamo, perché, per quanto tempo e quali sono i tuoi diritti.</p>

      <h2>Chi siamo</h2>
      <p>Kleurhoek è un sito olandese. Per domande sulla privacy, usa il nostro <Link href={contact("privacy")}>modulo di contatto</Link>.</p>

      <h2>Visitare e colorare</h2>
      <p>Contiamo le visite in forma anonima: senza cookie, senza indirizzi IP e senza nulla che possa ricondurre a te. Non usiamo script pubblicitari o di tracciamento di terzi, nemmeno di Google, Meta o Pinterest. Puoi colorare, stampare e colorare insieme ad altri senza account. Quello che colori resta sul tuo dispositivo. Quando colori insieme ad altri, i tratti passano dal nostro server agli altri nella stanza, senza nomi; dopo 30 minuti senza che nessuno colori, la stanza si chiude. I nomi che scrivi per le etichette regalo non vengono mai inviati al nostro server.</p>
      <p>Per non contare due volte i visitatori, ogni giorno creiamo un codice a partire dal tuo indirizzo IP e dal tuo browser, con una chiave che cambia ogni giorno; l’indirizzo IP in sé non lo salviamo. Dopo 90 giorni sostituiamo quel codice con uno casuale, così che nemmeno noi possiamo più collegare un conteggio a un dispositivo. I conteggi in sé (quale pagina, quale paese, telefono o computer, quando) li conserviamo, per vedere come viene usato il sito nel corso degli anni.</p>

      <h2>Account</h2>
      <p>Gli account sono solo per adulti (dai 16 anni in su). I bambini non hanno bisogno di un account e non possono crearne uno. Se hai un account, conserviamo il tuo nome, il tuo indirizzo email e i tuoi preferiti, così li ritrovi su tutti i tuoi dispositivi. Puoi eliminare il tuo account da solo; insieme all’account vengono eliminati anche i tuoi preferiti e la tua iscrizione alle email.</p>

      <h2>Email</h2>
      <p>Se ti iscrivi alle nostre email, conserviamo il tuo indirizzo email, gli argomenti che scegli e il tuo paese e la tua lingua. Prima confermi l’iscrizione tramite un link. Le nostre email non contengono pixel di tracciamento né link reindirizzati per misurare se le apri. Puoi annullare l’iscrizione con un clic in fondo a ogni email, e a quel punto cancelliamo il tuo indirizzo.</p>

      <h2>Contatti</h2>
      <p>Se ci mandi un messaggio, usiamo il tuo nome e il tuo indirizzo email solo per risponderti. Conserviamo il messaggio per non più di dodici mesi.</p>

      <h2>Pinterest, Facebook e Instagram</h2>
      <p>Kleurhoek pubblica i propri disegni da colorare sui propri account di Pinterest, Facebook e Instagram. Per farlo, colleghiamo questi account tramite l’accesso ufficiale (OAuth) di Pinterest e Meta. Conserviamo in forma cifrata i token di accesso di questo collegamento e li usiamo solo per pubblicare post e creare bacheche sui nostri account. Non leggiamo, raccogliamo né conserviamo dati di altri utenti di questi servizi, e non usiamo il collegamento per la pubblicità. Il pulsante «Salva su Pinterest» sul nostro sito è un semplice link: non viene caricato alcuno script di Pinterest. Il collegamento può essere rimosso in qualsiasi momento, dopodiché cancelliamo i token.</p>

      <h2>Chi ci aiuta</h2>
      <p>Il sito è ospitato da Scaleway ad Amsterdam. Cloudflare si occupa di velocità e sicurezza, Zitadel dell’accesso e Brevo dell’invio delle nostre email. Trattano i dati solo per nostro conto e solo per questo scopo. Se clicchi su un link a un negozio, come Amazon, da quel momento si applica l’informativa sulla privacy di quel negozio.</p>

      <h2>I tuoi diritti</h2>
      <p>Puoi chiederci quali dati abbiamo su di te e farli correggere o cancellare. Per farlo, <Link href={contact("privacy")}>contattaci</Link>. Se non sei d’accordo con il modo in cui trattiamo i tuoi dati, puoi presentare un reclamo all’Autoriteit Persoonsgegevens (l’autorità olandese per la protezione dei dati) o all’autorità del tuo paese.</p>

      <h2>Modifiche</h2>
      <p>Se cambia qualcosa in ciò che conserviamo, aggiorniamo questa pagina. La data in alto indica quando è stata aggiornata l’ultima volta.</p>
    </>
  );
}

export const text: PrivacyText = { title: "Informativa sulla privacy", description: "Quali dati conserva Kleurhoek, perché e per quanto tempo: niente cookie, conteggio anonimo delle visite e account solo per adulti.", Body };
