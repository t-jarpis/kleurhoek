# Architectuur

Het volledige architectuurdocument met diagrammen staat hier: https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ

**Afspraak:** bij elke architectuurwijziging worden het document én de diagrammen bijgewerkt, en komt er een ADR in `docs/adr/`.

## Kort
- Website en admin panel in Next.js, API in NestJS als modulaire monoliet met domeinen: Identiteit en toegang, Catalogus, Lokalisatie, Beschikbaarheid, Analytics, Organisaties, Contact, Bronnen, Berichten (fase 1); Betrokkenheid, Rechten en abonnementen (fase 2); Betalingen (fase 3); Winkel (fase 4).
- Inloggen via Zitadel Cloud, organisatie `Kleurhoek` in de gedeelde instance per omgeving. Gedeelde code uit `t-jarpis/platform`.
- Scaleway Amsterdam (eigen organisatie, een project per omgeving), Cloudflare (eigen zone), PostgreSQL met een schema per domein en row-level security op `tenant_id`.
- Analytics zonder cookies en zonder persoonsgegevens. Accounts alleen voor volwassenen (16+ in NL).
- Kleurhoek is een verkoopbare eenheid: alle data, domeinen en registraties staan apart.
- Stijl via `packages/theme`: tokens en fonts per thema, componenten lezen alleen semantische variabelen; nu het thema Studio (ADR 0012, 0016).
- Website afschermen met een IP-lijst uit het admin panel, gehandhaafd door de website-proxy (ADR 0015). Rooktests na een deploy mogen erlangs met een geheime controlesleutel (`x-kh-check`, per omgeving uit Terraform).
- Organisaties (scholen, opvang …) met eigen huisstijl, aanbod, functies en `{code}.kleurhoek.nl` via een Cloudflare Worker; in te stellen in het admin panel (ADR 0017).
- Eigen inlogpagina op `login.kleurhoek.nl` (login v2 via de Session API van Zitadel): e-mailcode en passkeys, in de huisstijl van de organisatie (ADR 0018).
- Releases: browsertest in CI vóór de uitrol, Deploy pas na groene CI, browsertest na de uitrol met automatisch terugdraaien; migraties altijd uitbreidend (ADR 0019).
- Dashboard met grafieken over 7 dagen tot 12 maanden, paginasoort per weergave, accountcijfers (nieuw, actief, terugkerend) zonder extra persoonsgegevens (ADR 0020).
- Productie op www.kleurhoek.nl (kale domein, .be en .com sturen door): kleine database met back-up in een ander datacenter, API en website naar nul zolang het rustig is, catalogus bij elke start, uitrollen naar prod met goedkeuring (ADR 0021).
- Doelen voor bezoeken, platen en doorkliks per maand, met grafiek en stand van deze maand in het admin panel (ADR 0022).
- Releasenotes per uitrol in het admin panel, vastgelegd door de API bij het opstarten; uitrollen en bouwen in één job, dus één goedkeuring voor prod (ADR 0023).
- Contact: formulier op de website, inbox met notities en status in het admin panel, kanalen (web nu, WhatsApp als volgende stap), gesprekken 12 maanden bewaard (ADR 0024).
- Bronnengids: thema's met alleen links naar kleurplaten bij de makers zelf (nooit hun beeld), goedkeuring in het admin panel, dagelijkse controle die verdwenen bronnen offline haalt, producten per thema (ADR 0025).
- Disclaimer en voettekst op elke pagina; nieuwe platen via `scripts/plates` (preview en ingest) (ADR 0026).
- Meer soorten werkjes (vouwblad, werkblad, sjabloon, kaart, tekenles), moeilijkheid, extra pagina's met antwoordblad, leeftijd 12+, en een kwaliteitscontrole voor de hele catalogus (ADR 0027).
- Pagina Eigen omgeving met de voordelen voor scholen, opvang en verenigingen en een aanvraagformulier; aanvragen komen in de inbox en worden met één klik een organisatie (ADR 0028).
- Tekstlaag: teksten in platen blijven in het Nederlands in de SVG en worden bij het serveren vertaald uit een woordenlijst per taal (`texts/<taal>.json`), met kleinere letter als de vertaling langer is; adres per taal met hash; taalgebonden platen alleen in de brontaal; controle per taal met `check-lang.mjs` (ADR 0029).
- Publieke releasenotes: trailer `Public-note:` met een tekst voor bezoekers, voorlopig alleen zichtbaar in het admin panel (blok "Voor bezoekers" bij Releases); later eventueel een pagina "Wat is er nieuw" (ADR 0030).
- Winkel per land: Amazon-winkels per land, snel toevoegen met een ASIN voor meerdere winkels, productlijst met aan/uit en filter per land, matrix "Per land", landen per product als vinkjes; materiaal stempels (ADR 0031).
- Binnenkomst: .be en .com sturen door met `?via=`; de site telt bij de eerste paginaweergave van buitenaf het domein en de hostnaam van de verwijzer, zonder cookies; dashboard "Binnengekomen via domein" en "Verwijzende sites" (ADR 0032).
- Opbrengst per klik: rapporten van partners (CSV) inlezen in het admin panel; verkopen en commissie per partner, product en plaat naast de doorkliks, met opbrengst per klik (ADR 0033).
- Analytics als eigen sectie in het admin panel (bezoekers, bronnen, inhoud, apparaten en landen, organisaties, nu op de site); eigen domein met een vast contract, met een groeipad van Postgres via partities en een wachtrij naar een eigen dienst (ADR 0034). Zijmenu in groepen met eigen iconen.
- Vindbaarheid: alleen www.kleurhoek.nl in productie wordt geïndexeerd; dev, lokaal en organisaties krijgen noindex en een afgeschermde robots.txt. Sitemap met taalversies, canonieke URL's, plaatomschrijving per taal en gestructureerde gegevens; verificatiecodes en voorpaginatekst per markt in het admin panel (ADR 0035).
- Instellingen per organisatie: leerdoelen afgeleid uit soort, onderwerp en naam; collecties in Catalogus; aanbod beperkt tot collecties, leerdoelen en zonder uitgezette platen; filter Leerdoel per organisatie; beheerders van een school (websiteaccounts) stellen dit zelf in via Beheer op de eigen site (ADR 0036).
- Mail (domein Berichten): aanmelden met bevestiging (16+), voorkeuren en afmelden met één klik, templates als blokken per taal, workflows (aanleiding + stappen), campagnes en een wachtrij. Alles zelf gebouwd; afleveren via SMTP achter één adapter (lokaal Mailpit). Geen tracking; afmelden verwijdert de abonnee (ADR 0037).
