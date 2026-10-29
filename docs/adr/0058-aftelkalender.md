# 0058 · Aftelkalender in december

- Status: aangenomen
- Datum: 2026-10-30

## Context
Een plaat per dag in december laat kinderen elke dag terugkomen, en ouders, scholen en blogs delen en linken zo'n kalender.

## Besluit
- **De pagina.** `/aftelkalender` per markt heeft 24 deurtjes, door elkaar zoals bij een echte kalender. De volgorde verschilt per jaar maar ligt vast binnen een jaar.
- **Welke plaat achter welk deurtje** (`lib/advent.ts`):
  - Waar Sinterklaas (of Nikolaus, Mikołaj …) gevierd wordt, zijn de eerste dagen voor Sinterklaas.
  - Daarna wisselen kerst (en chanoeka) en winterplaten elkaar af, met de mooiste kerstplaat op 24 december.
  - De winterplaten komen uit een vaste, nagekeken lijst.
  - Waar geen kerst gevierd wordt (Turkije), telt de kalender af naar oud en nieuw.
  - Alleen platen die in die markt zichtbaar zijn, dus feestdagen en taal kloppen vanzelf (ADR 0053, 0054).
- **Wanneer de deurtjes opengaan.** Dat volgt de datum van de markt (de seizoensdata van de API):
  - in november zijn alle deurtjes dicht en telt de pagina af;
  - in december gaat er elke dag één open;
  - na de 24e en de rest van het jaar staan alle deurtjes open, als de kalender van afgelopen december.

  Welke deurtjes je al open hebt gemaakt, onthoudt alleen het apparaat.
- **Ingang.** In november en december staat er een blok op de voorpagina. Verder is de kalender te vinden in de footer, de sitemap en llms.txt.
- **Design system.** Nieuwe component AdventCalendar en icoon `calendar`.

## Gevolgen
- Nieuwe winter- en kerstplaten komen vanzelf in de kalender als ze in de lijst staan of een feestdag hebben.
