import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Disclaimer", description: "Wat je met de kleurplaten van Kleurhoek mag doen, hoe we naar andere sites linken en hoe je ons iets meldt." };

/** Disclaimer (ADR 0026). Tekst in het Nederlands; andere markten krijgen hun eigen versie zodra ze live gaan. */
export default async function DisclaimerPage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org) notFound();
  const t = messages(marketLanguage(market));
  const contact = (topic?: string) => `/${market}/contact${topic ? `?onderwerp=${topic}` : ""}`;
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "disclaimer" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={`/${market}`}>{t.back}</a></header>
      <h1 className="page-title">Disclaimer</h1>
      <article className="kh-prose">
        <p className="kh-meta">Laatst bijgewerkt op 24 oktober 2026.</p>
        <p>Op deze pagina lees je wat je met de kleurplaten en knutselplaten van Kleurhoek mag doen, hoe wij naar andere websites linken en hoe je ons iets meldt. Door Kleurhoek te gebruiken ga je akkoord met deze afspraken.</p>

        <h2>Alles is zelf getekend</h2>
        <p>Alle kleurplaten, knipplaten en bouwplaten op Kleurhoek zijn speciaal voor Kleurhoek getekend. We kopiëren geen tekeningen van andere websites of uit boeken, en we tekenen geen bekende figuren, merken of personages na. Het auteursrecht op de tekeningen en op deze website ligt bij Kleurhoek.</p>
        <p>Je mag de platen gratis gebruiken:</p>
        <ul>
          <li>thuis, om in te kleuren, te printen en uit te delen aan familie en vriendjes;</li>
          <li>op school, in de kinderopvang, bij een vereniging of in de bibliotheek, ook in grote aantallen;</li>
          <li>op een feestje, bijvoorbeeld als knutselactiviteit.</li>
        </ul>
        <p>Dit mag niet zonder onze schriftelijke toestemming: platen verkopen (los, in een boekje of als download), ze op een andere website, in een app of op sociale media zetten als eigen materiaal, of ze gebruiken in producten of reclame. Delen mag wel met een link naar de plaat op Kleurhoek.</p>

        <h2>Thema&apos;s bij de maker</h2>
        <p>Kinderen zoeken vaak kleurplaten van figuren uit een tekenfilm, een pretpark of een boek. Die tekeningen zijn van de makers en die mogen wij niet zelf maken of kopiëren. Veel makers bieden ze wel gratis aan op hun eigen website. Onder <Link href={`/${market}/themas`}>Thema&apos;s bij de maker</Link> verzamelen we links naar die pagina&apos;s. Daarbij geldt:</p>
        <ul>
          <li>We linken alleen naar de officiële website van de maker of rechthebbende, nooit naar sites die tekeningen van anderen overnemen.</li>
          <li>We tonen geen afbeeldingen, tekeningen of logo&apos;s van de maker en slaan ze ook niet op. Je ziet bij ons alleen een eigen beschrijving en een link. Alleen als een maker ons daar schriftelijk toestemming voor geeft, kan dat anders zijn; dat staat er dan bij.</li>
          <li>Elke link wordt door ons bekeken voordat hij online komt. Een computerprogramma controleert daarna elke dag of de pagina nog bestaat. Verdwijnt een pagina, dan halen we de link automatisch weg. We volgen daarbij altijd de regels (robots.txt) van de website van de maker.</li>
          <li>De inhoud van de websites van makers valt onder hun eigen verantwoordelijkheid en voorwaarden. Wij hebben daar geen invloed op.</li>
        </ul>
        <p>Ben je een maker en wil je dat we een link aanpassen of weghalen, of wil je juist samenwerken? <Link href={contact("partnership")}>Neem contact met ons op</Link>. We passen het binnen vijf werkdagen aan.</p>

        <h2>Merken en namen</h2>
        <p>Namen van figuren, pretparken, series en merken zijn van hun eigenaren. We gebruiken ze alleen om te beschrijven waar je iets kunt vinden. Kleurhoek is niet verbonden aan deze eigenaren en wordt niet door hen gesponsord, tenzij dat er uitdrukkelijk bij staat.</p>

        <h2>Partnerlinks</h2>
        <p>Bij sommige platen en thema&apos;s noemen we spullen die je erbij kunt gebruiken, zoals een kinderschaar of kleurpotloden. Dat zijn partnerlinks: als je via zo&apos;n link iets koopt, krijgt Kleurhoek een kleine vergoeding van de winkel. Jij betaalt hetzelfde. Zo blijven de platen gratis. Partnerlinks staan altijd duidelijk aangegeven. De winkel is verantwoordelijk voor het product, de prijs en de levering.</p>

        <h2>Auteursrecht melden</h2>
        <p>Denk je dat er op Kleurhoek iets staat waar jij de rechten op hebt, of dat een link naar iets verwijst wat niet zou mogen? Meld het via het <Link href={contact("copyright")}>contactformulier</Link> met als onderwerp &quot;Auteursrecht&quot;. Vermeld om welke pagina het gaat, waarom het volgens jou niet klopt en hoe we je kunnen bereiken. We reageren binnen vijf werkdagen en halen het weg zolang we het uitzoeken als daar reden voor is.</p>

        <h2>Veilig knutselen</h2>
        <p>Knip- en bouwplaten zijn bedoeld om samen met een volwassene te maken. Gebruik een kinderschaar en, bij lampionnen, altijd een ledlampje en nooit een echte kaars. Kleine onderdelen zijn niet geschikt voor kinderen onder de drie jaar.</p>

        <h2>Aansprakelijkheid</h2>
        <p>We maken Kleurhoek met veel zorg, maar we kunnen niet beloven dat alles altijd foutloos is of dat de website altijd bereikbaar is. Voor zover de wet dat toestaat, is Kleurhoek niet aansprakelijk voor schade die ontstaat door het gebruik van de website, de platen of de websites waar we naar linken.</p>

        <h2>Privacy</h2>
        <p>We gebruiken geen tracking-cookies en geen advertentienetwerken. We tellen bezoeken anoniem: zonder cookies, zonder IP-adres en zonder iets wat naar jou terug te leiden is. Een account is niet nodig. Stuur je ons een bericht, dan gebruiken we je naam en e-mailadres alleen om je te antwoorden en bewaren we het bericht hooguit twaalf maanden. Wil je dat we je bericht eerder verwijderen? <Link href={contact("privacy")}>Laat het ons weten</Link>.</p>

        <h2>Wijzigingen en vragen</h2>
        <p>We kunnen deze disclaimer aanpassen, bijvoorbeeld als er iets nieuws op Kleurhoek komt. Bovenaan staat wanneer hij voor het laatst is bijgewerkt. Op deze disclaimer is Nederlands recht van toepassing. Vragen? <Link href={contact()}>Neem contact met ons op</Link>.</p>
      </article>
      <SiteFooter market={market} t={t} />
    </div>
  );
}
