# 0054 · Europa compleet: Servisch, Macedonisch, Albanees, IJslands, en een controle op de kalender

- Status: aangenomen
- Datum: 2026-10-29

## Context
Na ADR 0053 hadden alle EU-landen een markt. In Europa ontbraken nog Servië, Noord-Macedonië, Albanië met Kosovo, en IJsland. Rusland en Belarus blijven buiten beschouwing vanwege de sancties. Bij elke nieuwe batch moesten kalender, tijdzone en seizoen met de hand worden aangevuld. Een vergeten land viel zonder melding terug op UTC, of op "alle feestdagen".

## Besluit
- **Nieuwe markten:** sr-rs, mk-mk, sq-al en is-is.
  - **Servisch** is in het Latijnse schrift. Zo zoeken Serviërs online ("bojanke"), al is Cyrillisch het officiële schrift.
  - **Albanees** dient ook Kosovo. Bezoekers uit Kosovo met Albanees als taal komen op sq-al (`bestMarket`), en de taalcodes `sr`, `mk`, `sq` en `is` hebben elk een eigen thuismarkt.
- **Orthodoxe kalender:**
  - Servië en Noord-Macedonië vieren Pasen op de orthodoxe datum.
  - Kerst valt op 7 januari in Servië, Noord-Macedonië en Montenegro.
  - IJsland krijgt Driekoningen, Hemelvaart, Pinksteren, vaderdag in november en de eerste schooldag eind augustus.
- **Kalendercontrole** (`apps/api/test/countries.test.ts`): voor elk land met een markt moet het volgende in orde zijn, anders faalt `pnpm check`:
  - een tijdzone,
  - een seizoen,
  - een eigen eerste schooldag,
  - alle algemene feesten: oud en nieuw, Valentijn, moederdag en vaderdag, Halloween, de feesten van andere geloven en verjaardagen.
  - Kerst en Pasen horen er ook bij, behalve in Turkije (ADR 0053).

  `ZONES` wordt daarvoor geëxporteerd.
- De test van de tekstlaag gebruikt nu een verzonnen land (ZZ). Echte landen hebben een eigen kalender, en dan valt de lampion-plaat onder Sint-Maarten.

## Gevolgen
- Er zijn 57 markten in 29 talen. Op Rusland en Belarus na heeft elk Europees land een markt.
- Een nieuwe markt zonder volledige kalender kan niet meer ongemerkt live.
