# 0029 · Tekstlaag in platen en meer talen

- Status: aangenomen
- Datum: 2026-10-24

## Context
Kleurhoek gaat naar alle Europese talen. Platennamen, woord en telvraag stonden al per taal (ADR 0003), maar ongeveer de helft van de platen heeft tekst ín de tekening: titels, uitleg, "knippen / vouwen / lijmen", "Voor: / Van:", namen op onderdelen. Die tekst zat vast in de SVG, in het Nederlands.

## Besluit
- **De SVG blijft in de brontaal (nl).** Elke `<text>` is een vertaalbare zin; we hoeven de tekeningen niet opnieuw te maken.
- **Woordenlijst per taal**: `packages/catalog-data/texts/<taal>.json`, van bronzin naar vertaling. Dezelfde zin hoeft één keer vertaald te worden, hoe vaak hij ook voorkomt (1.050 platen hebben samen zo'n 1.950 verschillende zinnen). De seed zet de lijst in Lokalisatie (soort `text`, sleutel = de bronzin) en werkt, anders dan de rest, gewijzigde vertalingen bij.
- **Vertalen bij het serveren.** De API vervangt elke tekst door de vertaling (`localizeSvg` in `@kleurhoek/catalog-data/text-layer.js`, gedeeld met de scripts). Is de vertaling langer, dan wordt de letter kleiner in dezelfde verhouding, zodat hij in dezelfde ruimte past.
- **Neutraal**: tekst zonder letters (cijfers, sommen) en één losse letter (label A, B) wordt niet vertaald.
- **Adres per taal**: `/v1/assets/plates/<slug>/<versie>.<taal>-<hash>.svg`. De hash komt uit de vertaalde zinnen van die plaat; een betere vertaling geeft een nieuw adres, zodat het CDN elk adres voor altijd mag bewaren. Zonder taal blijft het `<versie>.svg` (brontaal).
- **Zichtbaar in een taal** (aanvulling op ADR 0003): naam vertaald én elke tekst in de plaat staat in de woordenlijst van die taal.
- **Taalgebonden platen** (`languageBound` in `plates.json`): woordzoekers, schrijfletters, rijmen, geheimschrift. Die werken alleen in de taal waarin ze gemaakt zijn en krijgen geen naam in een andere taal. Voor een andere taal maken we een eigen versie met de generators.
- **Controle per taal**: `node scripts/plates/check-lang.mjs <taal>` meldt ontbrekende zinnen, platen die al een naam hebben maar nog niet zichtbaar zijn, en vertaalde tekst die buiten het vel valt of kleiner wordt dan 4,5 (dan een kortere vertaling kiezen). `--missing <bestand>` geeft de zinnen die nog vertaald moeten worden.
- **Volgorde van talen**: eerst Duits, Frans, Engels, Spaans, Italiaans en Pools, daarna de overige EU-talen. Een markt (land + taal) gaat pas live als interface, categorieën en een flink deel van de platen vertaald zijn.

- **Website en inlogpagina**: interfaceteksten per taal in `apps/web/src/i18n/<taal>.ts` (zelfde sleutels als `nl.ts`, gecontroleerd door TypeScript), de disclaimer per taal in `i18n/disclaimer/<taal>.tsx`. De inlogpagina (`apps/login`) kiest de taal uit `ui_locales` van het inlogverzoek of de browser en bewaart die in de flow; een nieuw account krijgt die taal als voorkeurstaal in Zitadel (voor de e-mails).

## Gevolgen
- Geen databasewijziging: de woordenlijst gebruikt de bestaande tabel `localization.translations`.
- De API houdt per plaatversie de lijst met zinnen in het geheugen en de woordenlijst een minuut.
- Nieuwe platen hoeven niets extra's te doen; nieuwe zinnen verschijnen vanzelf in `check-lang.mjs --missing`.
- Vertalingen van zinnen in de woordenlijst zijn machinaal gemaakt en daarna gecontroleerd met de render-controle. Een moedertaalspreker kijkt ze na voordat een markt live gaat.
