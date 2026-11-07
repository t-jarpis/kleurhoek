# 0090 · Illustratiestijl voor nieuwe platen

- Status: aangenomen
- Datum: 2026-11-07

## Context
Thijs vond dat onze platen eruitzien alsof een kind ze tekende: losse rechthoeken, cirkels en rechte poten. Kleurplaatsites die hoog in Google staan, hebben schattige, getekende figuren. Een beeldgenerator past niet bij ADR 0027 (eigen tekeningen als SVG-code) en geeft geen gesloten vlakken. We bleven dus bij tekenen in code, maar met een betere werkwijze.

## Besluit
- Nieuwe platen gebruiken de **illustratiekit** `scripts/plates/generators/illu.py`:
  - vloeiende vormen door punten (Catmull-Rom naar Bezier) met een heel licht trillende lijn, met een vaste seed zodat een plaat altijd hetzelfde wordt;
  - vaste onderdelen in één stijl: ogen met glimlichtjes, blaadjes, varens, graspolletjes, wolkjes, bloemetjes, schubjes;
  - een **inktrand** om de hoofdvormen van een figuur die aan de schaduwkant (rechtsonder) dikker wordt;
  - **penseelstreken** voor details: dun begin, dikker midden, dun einde.
- Inktrand en penseelstreken zijn zwarte vormen (`dot`), geen vlakken. Ze vragen geen nieuwe CSS, tellen niet als vlak en sluiten nooit een vlak af. Online kleuren, kleur-op-nummer, het ingekleurde voorbeeld en de PNG werken dus zoals altijd.
- De stijl staat in het design system als PlateIllustration: verhoudingen van figuren, lijndiktes, rustige achtergrond.
- Werkwijze per plaat: tekenen, renderen, kijken en verbeteren, minstens drie rondes, daarna `check.mjs`.
- De generator per serie staat ernaast, eerst `illu_dinos.py`. Eerste plaat: Babydino met een ijsje.

## Gevolgen
- De keuze voor dun, normaal of dik in de studio verandert de gewone lijnen, maar niet de extra dikte van de inktrand en de penseelstreken.
- Bestaande platen blijven zoals ze zijn. Een serie opnieuw tekenen in deze stijl is een aparte keuze.
- Een beeldgenerator gebruiken is nog steeds niet afgesproken. Een proef daarmee komt in een eigen ADR.
