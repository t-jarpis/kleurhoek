# 0076 · Het boekje als printlijstje

- Status: aangenomen
- Datum: 2026-11-03

## Context
Een bezoeker print gemiddeld 1 à 2 platen. Na het printen is de taak van een ouder klaar, en de site biedt dan niets aan. Thijs wil meer prints per bezoek, maar zonder iets toe te voegen wat de bezoeker vervelend vindt. Er bestond al een boekje: op de voorpagina platen kiezen en alles in één keer printen (`/boekje?platen=…`). Dat zat alleen verstopt achter een aparte kiesstand op de voorpagina.

## Besluit
- **Het boekje wordt het printlijstje.**
  - Bij elke plaat staat een knop "In mijn boekje".
  - Zolang er iets in het boekje staat, is er onderin elke pagina een klein balkje met "Bekijk en print" en "Leegmaken" (dat eerst om bevestiging vraagt). Op het boekje zelf staat het niet.
  - De PickBar staat daarvoor in de layout in plaats van alleen op de voorpagina.
- **"Nog eentje erbij?"** verschijnt pas na een tik op Printen, één keer, onder de printknop.
  - Het toont drie platen uit hetzelfde onderwerp, eerst van dezelfde soort en leeftijd.
  - Er is geen pop-up of venster: niets blokkeert en niets verdwijnt vanzelf.
  - "Print ze samen" opent `/boekje?platen=…&los=1`: alleen die platen, zonder voorblad, en het eigen boekje blijft zoals het was.
- **Het boekje** krijgt "Voorblad meeprinten" (standaard aan; uit bij `los=1`).
- **Alles blijft op het apparaat** (`kh:boekje`), zonder account en zonder cookies (ADR 0002).

## Gevolgen
- Het effect zien we aan prints en downloads per bezoek in de dagtotalen. Een print van een boekje telt nu als één print zonder plaat, net als voorheen.
- De kiesstand op de voorpagina blijft bestaan voor wie snel veel platen wil aantikken.
