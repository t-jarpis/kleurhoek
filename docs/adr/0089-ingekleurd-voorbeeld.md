# 0089 · Ingekleurd voorbeeld in de kleurstudio

- Status: aangenomen
- Datum: 2026-11-07

## Context
Een kind print een plaat zwart-wit met nummers en wil op het scherm zien welke kleur waar hoort. Wie een kleurenprinter heeft, wil soms de plaat ingekleurd op papier. De studio liet alleen je eigen kleuren zien en printte leeg of je eigen werk.

## Besluit
- Het ingekleurde voorbeeld is de plaat in zijn eigen kleuren: elk genummerd vlak in de kleur van zijn nummer, vlakken zonder nummer wit (`exampleFills` in `lib/studio.ts`). Het komt uit dezelfde gegevens als kleur-op-nummer; er is geen apart plaatje nodig.
- In de zijbalk staat onder het palet "Zo ziet hij eruit" met een klein vel (ColorExample in het design system). Tikken of "Groot bekijken" toont het voorbeeld groot op de plek van de plaat; "Terug naar mijn plaat" zet het terug. Niet in het Atelier en niet bij lijn trekken; alleen bij platen met nummers.
- "Printen" heeft drie keuzes: **Leeg** (bij kleur op nummer met nummers en kleurenlijst), **Voorbeeld in kleur** (zonder nummers) en **Ingekleurd** (je eigen werk, alleen als je al gekleurd hebt). Zonder eigen kleuren staat Leeg aan.
- Teksten in alle 29 talen.

## Gevolgen
- Het werk op het scherm blijft altijd staan, wat je ook print of bekijkt.
- Bij een leeg vel met nummers staat de kleurenlijst nu ook als je nog niets gekleurd hebt.
