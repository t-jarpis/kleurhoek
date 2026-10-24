# Architectuur

Het volledige architectuurdocument met diagrammen staat hier: https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ

**Afspraak:** bij elke architectuurwijziging worden het document én de diagrammen bijgewerkt, en komt er een ADR in `docs/adr/`.

## Kort
- Website en admin panel in Next.js, API in NestJS als modulaire monoliet met domeinen: Identiteit en toegang, Catalogus, Lokalisatie, Beschikbaarheid, Analytics, Organisaties, Contact, Bronnen (fase 1); Betrokkenheid, Rechten en abonnementen (fase 2); Betalingen (fase 3); Winkel (fase 4).
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
