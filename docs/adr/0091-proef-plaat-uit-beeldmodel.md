# 0091 · Proef: een plaat uit een beeldmodel

- Status: aangenomen (proef)
- Datum: 2026-11-07

## Context
ADR 0027 zegt: alle werkjes zijn eigen tekeningen als SVG-code, geen beeldgenerator. ADR 0090 maakte die tekeningen schattiger, maar een beeldmodel tekent nog een stuk vloeiender. Thijs maakte met ChatGPT een lijntekening van een babydino met een ijsje, op basis van een opdracht die op ons formaat is gericht. Hij wil zien of bezoekers die vaker kiezen dan onze eigen tekeningen.

## Besluit
- Eén plaat als proef: **Dino likt aan een ijsje** (dino's, 6–9), naast onze eigen Babydino met een ijsje (ADR 0090). Dit is een uitzondering op ADR 0027 voor deze ene plaat.
- De bron staat in `scripts/plates/bronnen/` (lijntekening, grijswaarden). Ze is nagekeken: een eigen figuur, geen bekend personage of merk.
- `scripts/plates/generators/trace.py` zet een lijntekening om naar ons formaat:
  - de lijnen worden een inktlaag (`<g class="ink">`, één zwarte vorm);
  - de witte gebieden worden gesloten vlakken;
  - kiertjes in de lijnen worden eerst gedicht (`--kier`), zodat bijvoorbeeld een blaadje dat net open is toch een eigen vlak wordt;
  - wat dat dichten aan wit afsnoept, gaat terug naar het vlak ernaast, en de vlakken lopen onder de lijnen door.
  Online kleuren, kleur-op-nummer, het voorbeeld en de PNG werken daardoor zoals altijd.
- `beeldmodel_proef.py` maakt de plaat opnieuw uit de bron, met de kleurcodes per vlak en de teksten in alle talen.
- Meten: met de gewone cijfers per plaat in het admin panel (weergaven, prints, gekleurd, bewaard). Zo vergelijken we de twee dinoplaten.

## Gevolgen
- Rechten: volgens de voorwaarden van OpenAI hoort de uitvoer bij wie hem maakte (Thijs, dus Kleurhoek). Een beeld uit een model is waarschijnlijk niet auteursrechtelijk beschermd. Dat geldt eigenlijk ook voor onze SVG-code, en bij verkoop gaat de catalogus gewoon mee (ADR 0004).
- Op de site blijft staan dat de platen met hulp van AI gemaakt zijn en dat elke plaat is nagekeken.
- Na een paar weken beslissen we op basis van de cijfers:
  - stoppen, en dan blijft het bij deze ene plaat of gaat hij eraf;
  - of overstappen. Dan volgt een nieuwe ADR over de aanbieder, een eigen account met API-sleutel en de werkwijze, en wordt ADR 0027 aangepast.
