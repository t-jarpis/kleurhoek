# 0052 · Midden- en Zuidoost-Europa, Grieks, kleine landen en tekensets in de lettertypen

- Status: aangenomen
- Datum: 2026-10-26

## Context
Na ADR 0051 waren er 32 markten. De lettertypen (Manrope, Nunito) bevatten alleen de basis-Latijnse tekens. Daardoor vielen letters zoals ł, ą, ę (Pools), ő, ű (Hongaars), ș, ț (Roemeens) en alle Griekse letters terug op een ander lettertype van het systeem. Dat gebeurde midden in een woord.

## Besluit
- **Tekensets:** elk lettertype krijgt per tekenset een eigen bestand met `unicode-range`. Manrope krijgt latin, latin-ext, greek en cyrillic; Nunito krijgt latin, latin-ext en cyrillic. De bestanden komen uit Fontsource (SIL OFL). `font.json` vermeldt de tekensets, en `build.mjs` maakt per tekenset en gewicht een `@font-face`. De browser laadt alleen de tekensets die een pagina gebruikt; een Nederlandse pagina laadt dus niets extra.
- **Nieuwe talen:** Tsjechisch (cs-cz), Slowaaks (sk-sk), Hongaars (hu-hu), Roemeens (ro-ro en ro-md) en Grieks (el-gr en el-cy). Elke taal krijgt alle onderdelen: interface, disclaimer, taxonomie, platen en woordenlijst, gecontroleerd met `check-lang`.
- **Kleine landen in bestaande talen:** Malta (en-mt), Monaco (fr-mc), Andorra (es-ad) en San Marino (it-sm).
- **Kalenders:**
  - **Orthodox:** Roemenië, Moldavië, Griekenland en Cyprus vieren Pasen op de orthodoxe datum. Griekenland en Cyprus krijgen ook carnaval (Apokries) op de orthodoxe datum.
  - **Sint-Nicolaas:** Mikuláš in Tsjechië op 5 december. Mikuláš, Mikulás en Moș Nicolae in Slowakije, Hongarije, Roemenië en Moldavië op 6 december.
  - **Sint-Maarten en Dierendag:** in Tsjechië, Slowakije en Hongarije.
  - **Moederdag en vaderdag** volgen de eigen datum per land, zoals moederdag in mei in Hongarije en Roemenië en vaderdag op 19 maart in Andorra en San Marino.
  - Driekoningen, carnaval waar het leeft, een eerste schooldag per land en een tijdzone per land.
- **Vindbaarheid:** standaardteksten met de zoekwoorden van elk land, zoals "omalovánky", "omaľovánky", "színezők", "planșe de colorat" en "ζωγραφιές".

## Gevolgen
- Er zijn 43 markten in zeventien talen.
- Talen met Cyrillisch schrift (Bulgaars, Oekraïens, Servisch) kunnen later zonder werk aan de lettertypen. Nunito heeft geen Grieks; een organisatie die Nunito kiest, krijgt Grieks in het systeemlettertype.
