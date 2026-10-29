# 0059 · Lespakketten voor leerkrachten

- Status: aangenomen
- Datum: 2026-10-30

## Context
Leerkrachten zoeken kant-en-klaar materiaal per thema en groep. Dat is ook de opstap naar een eigen omgeving voor scholen (ADR 0017).

## Besluit
- **Samenstelling.** Per onderwerp en leeftijd een pakket (`lib/packs.ts`), afgeleid uit de platen zelf:
  - eerst kleurplaten (hooguit 3), dan werkbladen en spellen (hooguit 3), dan iets om te knutselen of te tekenen (hooguit 2), samen hooguit 8 platen;
  - alleen als er minstens 5 platen zijn, met minstens één kleurplaat en minstens één om te leren of te maken.
- **Pagina's.**
  - `/lespakketten` met een overzicht per leeftijd.
  - `/lespakketten/<onderwerp>-<leeftijd>` met een blok "Voor de leerkracht" met de leerdoelen van de platen (ADR 0036), de platen in volgorde, en "Print het hele pakket", dat het boekje opent.
- **Vindbaarheid.** Gestructureerde gegevens als LearningResource. De pakketten staan in de sitemap en llms.txt.
- **Design system.** Nieuwe component PackCard met het blok Voor de leerkracht, en icoon `book`.

## Gevolgen
- Er is niets om te beheren: nieuwe platen komen vanzelf in de pakketten. Op de site van een organisatie gelden de platen uit haar eigen aanbod.
