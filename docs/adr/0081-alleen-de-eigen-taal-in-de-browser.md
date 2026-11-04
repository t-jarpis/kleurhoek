# 0081 · Alleen de eigen taal in de browser

- Status: aangenomen
- Datum: 2026-11-04

## Context
De client components van de website haalden hun teksten met `messages()` uit `i18n/nl.ts`. Dat bestand laadt alle 29 talen vooraf. Daardoor kreeg elke pagina, in elke markt, één gedeeld JavaScript-bestand met de teksten van alle talen mee: 622 kB, 350 kB gecomprimeerd voor de voorpagina in totaal. Op een telefoon kost dat merkbaar laadtijd, en Google rekent snelheid mee.

## Besluit
- **Teksten van één taal.** De Nederlandse teksten en het type `Messages` staan in `i18n/nl-base.ts`. De varianten per markt staan in `i18n/variants.ts`: en-US, de-CH/LI, en-CA, fr-CA en Latijns-Amerikaans Spaans. Server en browser gebruiken dezelfde varianten.
- **Server blijft zoals het was.** Server components gebruiken `messages()` uit `i18n/nl.ts`, met alle talen vooraf; de grootte van de serverbundel maakt niet uit.
- **Browser laadt per taal.** `i18n/load.ts` laadt alleen de taal van de pagina, als eigen bestand, met de variant van de markt erop.
  - De layout zet `I18nProvider` (components/I18n.tsx) om de pagina. Die wacht met `use()` op die ene belofte per markt.
  - Client components lezen de teksten met `useT()`.
  - Server en browser renderen dezelfde tekst, dus er is geen flits en geen mismatch bij hydratie.
- **Taalbanner.** Die toont tekst in de taal van de browser, niet van de pagina. Hij krijgt per taal van de site alleen zijn vier teksten van de server mee.
- **Test.** Een test houdt `loadMessages()` gelijk aan `messages()` voor elke markt en taal.

## Gevolgen
- Voorpagina /nl-nl: van 1.121 kB naar 526 kB JavaScript; gecomprimeerd van 350 kB naar 163 kB.
- **Nieuwe client component:** gebruik `useT()`, nooit `messages()` uit `@/i18n/nl`. Type-imports mogen.
- **Nieuwe taal:** voeg hem toe aan `LANGUAGES` (variants.ts), de loaders in load.ts en `base` in nl.ts. De test faalt als een markt ontbreekt.
- Bij het hydrateren wacht de pagina tot het taalbestand binnen is (enkele tientallen kB). Daarvoor reageren knoppen nog niet.
