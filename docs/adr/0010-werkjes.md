# 0010 · Van kleurplaten naar werkjes

- Status: aangenomen
- Datum: 2026-10-22

## Context
Kleurhoek wordt breder dan kleurplaten: knipplaten, bouwplaten en spellen om te printen. Ze delen bijna alles met kleurplaten (leeftijd, onderwerp, feestdagen, beschikbaarheid per land, de kleurstudio, het boekje), maar hebben extra informatie nodig.

## Besluit
- **Eén catalogus, met een soort per plaat**: `kleurplaat`, `knipplaat`, `bouwplaat`, `spel`. Geen apart domein: alle bestaande regels (vertalingen, beschikbaarheid, analytics, boekje, koelkast) werken meteen ook voor knutselwerk. Op de site heet het filter "Soort": Alles, Kleurplaten, Knutselen.
- **Extra per plaat**: tijd in minuten, of er een volwassene bij moet (schaar, mesje), papieradvies (grammen), een stappenplan en printadvies (vertaald, in Lokalisatie), en de **materialen** die je nodig hebt (`catalog.materials`, `catalog.plate_materials`). Kleurplaten krijgen standaard kleurpotloden (en optioneel stiften).
- **Tekening op A4-verhouding**: de breedte blijft 200, de hoogte verschilt per versie (`plate_versions.height`, kleurplaten 200, de lampion 270). Studio, boekje en koelkast lezen de hoogte uit de plaat.
- **Vaste lijnstijlen** in de SVG: `.cut` (streepjes, knippen), `.fold` (stippels, vouwen), `.glue` (grijs vlak, lijmen) en `.tip` (korte uitleg). Dezelfde stijl staat in de API (voor `<img>` en het CDN) en in de CSS van de site. De datatest eist dat elk knutselwerk een kniplijn en stappen heeft.
- **De seed vult aan**: nieuwe platen, materialen en vertalingen komen er bij elke deploy bij; wat er al staat (ook wat in het admin panel is aangepast) blijft staan.
- Eerste knutselwerk: **lampion om te maken** voor Sint-Maarten (6–9 jaar, 30 minuten, met hulp, 160 gram).

## Gevolgen
- Een knutselwerk kun je eerst inkleuren in de studio (vrij of op nummer) en dan printen, knippen en vouwen.
- Stappen en materialen staan bij de plaat in een blok "Voor ouders", onder de studio.
