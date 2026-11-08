# 0094 · Leeftijd uit de tekening, en landnamen in de taal van de markt

- Status: aangenomen
- Datum: 2026-11-08

## Context
Thijs zag dat platen voor 6–9 jaar niet ingewikkelder waren dan die voor 2–4 of 4–6. De cijfers bevestigden dat: het mediane aantal vlakken was 12 (2–4), 19 (4–6), 21 (6–9) en 24 (9+). Een kwart van de 6–9-platen was eenvoudiger dan de gemiddelde plaat voor 2–4. De leeftijd was bij het maken vooral op onderwerp gekozen.

Daarnaast stonden landen bij platen (bijvoorbeeld "Verenigde Staten", "Brazilië") in elke taal in het Nederlands, omdat plates.json alleen de Nederlandse naam kent.

## Besluit
- **De leeftijd van een kleurplaat volgt uit het aantal vlakken** (`packages/catalog-data/age-rule.js`):

  | Leeftijd | Vlakken |
  | --- | --- |
  | 2–4 | tot en met 12 |
  | 4–6 | 13 tot en met 30 |
  | 6–9 | 31 tot en met 80 |
  | 9+ | 81 tot en met 200 |
  | 12+ | meer dan 200 |

  - De regel geldt niet voor knip-, bouw- en werkbladen of platen zonder vlakken: daar bepaalt het maakwerk de leeftijd.
  - `scripts/plates/ages.mjs --write` past de regel toe op plates.json. 313 platen kregen een andere leeftijd.
  - Migratie `0034_plate_ages` zet hetzelfde in de database. Alleen waar nog de oude leeftijd uit de catalogus staat; een keuze uit het admin panel blijft staan.
  - De test van catalog-data en `scripts/plates/check.mjs` falen als een nieuwe plaat niet bij de regel past.
- **Een kwaliteitslat vanaf 6 jaar.** Nieuwe platen voor 6–9 en ouder komen uit de illustratiestijl van ADR 0090 of de route via een beeldmodel van ADR 0091, niet meer uit de eenvoudige stijl. Het aantal 6–9-platen daalt daardoor eerst, en groeit daarna met betere platen.
- **Landnamen in de taal van de markt.** `countryName` in catalog-data koppelt de Nederlandse bronnaam aan een ISO-code en geeft de naam via `Intl.DisplayNames`. De API levert de namen mee in de taxonomie (`countries`). De site toont ze op kaarten, in de filterknoppen en in het zoeken. Het filter blijft op de bronnaam werken, dus links en filters veranderen niet.

## Gevolgen
- De leeftijdsfilters op de site tonen nu platen die echt bij de leeftijd passen; de aantallen per leeftijd verschuiven.
- Een nieuw land bij een plaat vraagt een regel in `countries.js`; de test meldt het als die ontbreekt.
