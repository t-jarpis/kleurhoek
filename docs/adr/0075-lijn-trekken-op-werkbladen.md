# 0075 · Lijn trekken op werkbladen

- Status: aangenomen
- Datum: 2026-11-03

## Context
Thijs merkte op dat je in een doolhof online geen lijn kunt trekken. Hetzelfde geldt voor andere werkbladen, spelletjes en tekenlessen: verbinden, overtrekken, woordzoekers, klokken, kamertje verhuren, stippen en spiegeltekenen. De studio kon alleen vlakken vullen. Penselen kon alleen in het Atelier en altijd binnen het vlak waar je begon; daar valt een weg door een doolhof niet onder.

## Besluit
- **Vrije lijn:** een streek met vlaknummer `-1` (`FREE_REGION`) hoort bij geen vlak. Hij komt boven de hele plaat, ook over de lijnen heen, zonder clip. De gum werkt alleen op deze lijnen. Vullingen blijven alleen in echte vlakken.
- **Stand "Lijn trekken"** in Zo kleur je, naast Vrij kleuren en Kleur op nummer (design system: LineMode). Hij is er alleen bij werkbladen, spelletjes en tekenlessen.
  - In deze stand tekent een veeg een stiftlijn in de gekozen kleur. Het gummetje in het palet gumt.
  - Hij staat meteen aan bij tekenlessen, doolhoven, verbinden, schrijven en woordzoekers.
- **Atelier:** een penseelstreek die buiten elk vlak begint, wordt ook een vrije lijn.
- **Samen kleuren** neemt vrije lijnen mee: de API staat `r: -1` toe voor streken, niet voor vullingen.

## Gevolgen
- Ongedaan maken, de time-lapse, opslaan en printen (ingekleurd) gaan vanzelf mee, omdat het gewone streken zijn.
- Een link met kleuren (ADR 0074) neemt de lijnen niet mee, net als penseelstreken.
- Kaarten en knip-, bouw- en vouwplaten krijgen de stand niet: daar teken je niet op het scherm, maar knip, vouw of schrijf je op papier.
