# 0017 · Organisaties: whitelabel voor scholen, opvang en anderen

- Status: aangenomen
- Datum: 2026-10-23

## Aanleiding
Kleurhoek wil scholen, kinderopvang, verenigingen en bedrijven aansluiten met een eigen versie van de site. Die heeft een eigen naam, logo en kleuren, een eigen (sub)domein en een eigen aanbod, en de webshop kan uit. Dat moet vanaf het begin goed in de opzet zitten, en in het admin panel in te stellen zijn zonder nieuwe build of Terraform-wijziging.

## Besluit
**Een organisatie is een domein binnen de Kleurhoek-tenant** (schema `organizations`, eigen tabellen, RLS zoals overal). Het is geen nieuwe tenant: de catalogus, vertalingen en markten blijven van Kleurhoek en worden gedeeld. Een organisatie heeft:
- naam, code (`slug`), soort (platform, school, opvang, vereniging, bedrijf, overig), actief ja/nee;
- **huisstijl**: thema, lettertype, hoofd- en accentkleur, naam in het logo of een eigen logo (PNG/WebP/JPEG/SVG, max. 256 kB; SVG zonder scripts, geleverd in een CSP-zandbak);
- **aanbod**: markten, onderwerpen, leeftijden, soort platen (kleur- of knutselplaten). `null` betekent alles, ook wat er later bij komt;
- **functies**: webshop en partnerlinks aan/uit, inloggen voor ouders aan/uit;
- **domeinen**: altijd `{code}.kleurhoek.nl` (dev: `{code}-dev.kleurhoek.nl`), plus eventueel eigen domeinen.

Kleurhoek zelf is de standaardorganisatie (`kleurhoek`, kan niet uit). Elk adres dat bij geen andere organisatie hoort, valt daaronder.

**Kleuren blijven toegankelijk.** Alleen hoofd- en accentkleur zijn per organisatie te kiezen; de rest komt uit het thema. De API weigert een kleur met te weinig contrast (hoofdkleur 3:1 tegen de achtergrond en 4,5:1 voor tekst erop; accent 4,5:1). Werkt een kleur alleen in licht, dan blijft in donker de themakleur staan. `brandCss()` in `@kleurhoek/theme` maakt de CSS, zowel voor de site als voor het live voorbeeld in beheer (met een `scope`).

**Website.** De proxy zet de host om naar een organisatie (cache 30 s) en schrijft intern om naar `/[org]/[market]/…`. Zo cachet Next.js per organisatie en kan een pad als `/de-regenboog/nl-nl` niet van buitenaf worden opgevraagd. De API filtert platen, onderwerpen, seizoenen en productlinks op het aanbod (`?org=`). Andere organisaties dan Kleurhoek krijgen `noindex`.

**Subdomeinen zonder Terraform.** Eén wildcard-record `*.kleurhoek.nl` wijst naar een Cloudflare Worker (`kleurhoek-organisaties`). Die stuurt door naar de website van de juiste omgeving, met de oorspronkelijke host, het IP-adres en het land, en een eigen geheim. De website vertrouwt die headers alleen met dat geheim (`ORG_WORKER_SECRET`), anders kon een bezoeker zelf een toegestaan IP-adres opgeven. Codes die op `-dev` eindigen zijn niet toegestaan, omdat ze in productie als dev-adres zouden gelden.

**Thema's in de browser.** Alle thema's en lettertypen staan in één `theme.css`: het standaardthema op `:root`, de andere onder `[data-kh-theme]` en `[data-kh-font]`. De browser laadt alleen de lettertypen die gebruikt worden. Dit vervangt "één thema per build" uit ADR 0016.

## Afwegingen
- *Een organisatie als tenant*: zuiverder gescheiden, maar dan zou elke school de catalogus, vertalingen en markten moeten kopiëren of delen over tenants heen. De tenant blijft de eenheid van verkoop (ADR 0004); de organisatie is een weergave.
- *Pagina's per organisatie in de URL* in plaats van alleen een header: de Next.js-cache weet dan zonder meer welke versie hij heeft.
- *Een Worker* in plaats van een Scaleway-domein per organisatie: Scaleway kent geen wildcard-domeinen. Per organisatie een domein koppelen zou een Terraform-run en een certificaataanvraag per school betekenen.
- *Eigen domeinen van organisaties* (bijv. `kleuren.deregenboog.nl`) vragen Cloudflare for SaaS (custom hostnames, de eerste 100 gratis). De app ondersteunt ze al (veld *Eigen domeinen*); de koppeling in Cloudflare volgt als een organisatie erom vraagt.
- *Inloggen per organisatie* staat standaard uit. De eigen inlogpagina neemt de huisstijl van de organisatie over (ADR 0018).
