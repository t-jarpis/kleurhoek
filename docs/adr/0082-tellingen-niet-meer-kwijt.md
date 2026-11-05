# 0082 · Tellingen niet meer stil kwijt, opslaan telt als download, Pinterest telt als gedeeld

- Status: aangenomen
- Datum: 2026-11-05

## Context
Tijdens de storing bij Scaleway op 5 november (ongeveer 10:00–11:30) gaf de API vaak een 503. De website gaf elke telling één keer door aan de API. Mislukte dat, dan was de telling weg, zonder dat het ergens te zien was.

Verder telde "Gedownload" sinds de pdf-knop verdween (22 oktober) niets meer: opslaan als afbeelding of filmpje werd niet geteld. En "Bewaar op Pinterest" telde niet als gedeeld.

## Besluit
- **Opnieuw proberen.** `lib/ingest.ts` (`send`) probeert een mislukte telling nog twee keer, na 0,3 en 1,2 seconde, met elk 3 seconden time-out.
  - Een 4xx (behalve 429) is een fout in het event zelf; die wordt niet opnieuw geprobeerd.
  - Lukt het niet, dan komt er één regel in de log, met alleen de soort telling en de foutcode, zonder bezoekersgegevens.
  - De bezoeker merkt hier niets van: de browser stuurt tellingen met `sendBeacon`.
- **Download.** Opslaan als afbeelding of als filmpje in de kleurstudio telt als `pdf_download`. De naam blijft, zodat de cijfers vergelijkbaar blijven. In het admin panel heet het "Gedownload: opgeslagen als afbeelding of filmpje".
- **Gedeeld.** "Bewaar op Pinterest" telt als `share`: op de computer bij het openen van Pinterest, op een telefoon als het deelmenu lukt. Analytics › Inhoud toont Gedeeld als kaart en als kolom bij de populairste platen.

## Gevolgen
- Een telling die ook na drie pogingen niet lukt, is nog steeds weg. Het is wel zichtbaar in de logs (Diagnose, zoekterm "Telling").
- Een wachtrij die tellingen bewaart tot de API weer werkt, komt pas als dit vaker voorkomt.
