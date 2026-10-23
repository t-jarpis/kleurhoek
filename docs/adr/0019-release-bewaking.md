# 0019 · Releases bewaken: browsertest vóór en na de uitrol, en automatisch terugdraaien

- Status: aangenomen
- Datum: 2026-10-23

## Aanleiding
Op 23 oktober stond dev een half uur zonder opmaak. Een lege tekst in de `<head>` gaf een hydratiefout in React, en daarbij verdween de stylesheet. Alle controles waren groen: typecheck, unit-tests, build en een rooktest die alleen keek of de server antwoordde. Wat een echte browser van de pagina maakt, controleerde niemand.

## Besluit
1. **Browsertest vóór de uitrol (CI, job `e2e`).** API (met PostgreSQL), website en inlogpagina draaien als productiebuild. `.github/e2e/run.sh` maakt een testschool met eigen huisstijl. Daarna opent Chrome deze pagina's: home, een plaat, het boekje, de home van de school en de inlogpagina. Elke pagina moet opmaak hebben en mag geen JavaScript-fouten geven, en de school moet haar huisstijl hebben (`.github/diagnose/browser-check.mjs`).
2. **Uitrollen pas na groene CI.** Deploy start via `workflow_run` op een geslaagde CI op `main` en rolt precies die commit uit. Handmatig starten (ook voor productie) kan nog steeds.
3. **Na de uitrol dezelfde browsertest** op de echte omgeving, na de rooktest.
4. **Automatisch terugdraaien.** Voor elke container bewaart Deploy de vorige image. Mislukt de rooktest of de browsertest, dan gaan alle containers terug naar die versie en wordt de run rood.
5. **Migraties zijn altijd uitbreidend** (kolommen en tabellen erbij, niets weg of hernoemd in dezelfde release). Daardoor kan de vorige versie van de API na een terugdraaiing nog met de database werken. Iets weghalen gebeurt in een latere release, als niets het meer gebruikt.

## Afwegingen
- *Het hele `docker compose`-stelsel in CI* (met Zitadel) test ook inloggen, maar duurt veel langer en hangt af van een externe image. Het admin panel en echt inloggen dekken we later met een aparte test tegen dev.
- *Terugdraaien zonder migraties terug* is een bewuste grens: een terugdraaiing van het schema is riskanter dan de vorige app-versie op een uitgebreid schema.
