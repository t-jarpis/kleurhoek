# 0098 · Kleurhoek wijst naar Denkhoek

- Status: aangenomen
- Datum: 2026-11-09

## Context
Denkhoek (www.denkhoek.nl, eigen repo `t-jarpis/denkhoek`) is de zustersite van Kleurhoek: gratis puzzels (sudoku, doolhof, woordzoeker, speurpuzzel, rekenpuzzels, nonogram, binaire puzzel), printbaar, zonder account, van dezelfde maker en in dezelfde familiestijl. Thijs wil dat bezoekers van Kleurhoek Denkhoek kunnen vinden. Denkhoek is er (nog) alleen in het Nederlands.

## Besluit
- **Twee plekken.** Een regel in de voettekst ("Ook van ons: Denkhoek – gratis puzzels") op elke pagina, en één rustige tegel op de voorpagina onder de onderwerplinks, vóór de koelkastdeur en het mailformulier. Nieuwe DS-component **SisterSite** (`.kh-sister`): beeldmerk van Denkhoek (blokjes blauw, teal, paars en amber uit de krijt-tokens), een vraag, één zin en een omlijnde knop. Neutraal vlak, geen krijtkleur als achtergrond, niet bij printen.
- **Alleen nl-NL en nl-BE**, en alleen op Kleurhoek zelf (`org.isDefault`), niet op de eigen omgeving van een organisatie. Andere markten tonen niets.
- **Eén plek voor markten en teksten:** `apps/web/src/lib/sister-sites.ts` met `DENKHOEK_MARKETS` en de teksten en het adres per taal. Een taal erbij = de markt aan de lijst toevoegen en een tekst in die taal. De teksten staan daar en niet in `i18n/`, zoals bij de Sinterklaaskalender (ADR 0065): `Messages` vraagt elke sleutel in alle 29 talen, terwijl dit maar in één taal getoond wordt.
- **Gewone link:** `target="_blank"` zoals de andere externe links, `rel="noopener"`, geen `nofollow` (eigen site) en geen `noreferrer`. Geen `?via=`: dat is bij Kleurhoek de code van het binnenkomstdomein (ADR 0032) en Denkhoek leest het niet. Denkhoek telt zelf de verwijzer; door `Referrer-Policy: strict-origin-when-cross-origin` ziet het alleen het domein (www.kleurhoek.nl of www.kleurhoek.be).
- Test `lib/sister-sites.test.ts`: alleen nl-NL en nl-BE, elke markt in de lijst is live en heeft een tekst, de link is gewoon (geen nofollow, noreferrer of tracking), niets op een eigen omgeving.

## Gevolgen
- `SiteFooter` krijgt een verplichte prop `market`.
- Kleurhoek telt het doorklikken naar Denkhoek niet zelf; de cijfers staan in het beheer van Denkhoek onder de verwijzende sites.
- Kleurhoek blijft los verkoopbaar: bij verkoop van een van beide sites is het weghalen één regel op de voorpagina en één in de voettekst (`lib/sister-sites.ts`, `components/SisterSite.tsx`).
- Andersom (Denkhoek naar Kleurhoek) hoort in de repo van Denkhoek.
