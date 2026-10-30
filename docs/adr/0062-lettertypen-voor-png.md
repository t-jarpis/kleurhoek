# 0062 · Complete lettertypen voor PNG-plaatjes

- Status: aangenomen
- Datum: 2026-10-30

## Context
De PNG-plaatjes van de API worden gemaakt met resvg. Dat zijn de plaatjes in mails (ADR 0037), de deelplaatjes (ADR 0055) en de Pinterest-pins (ADR 0057). In productie stond er geen tekst op: geen naam onder de pin en geen "Fijne kerst!" op een kaart. Lokaal ging het wel goed.

De oorzaak: de API gaf resvg de losse subsets van Nunito (Latijn, Latijn-uitgebreid, Cyrillisch). Die hebben allemaal dezelfde familienaam en hetzelfde gewicht, dus resvg kiest er één. Welke dat is, hangt af van het platform. In de Alpine-container (musl) kwam er geen tekst, en met een andere volgorde werden het blokjes. De tests draaiden op glibc en zagen het daarom niet.

## Besluit
- **Complete lettertypen.** In `apps/api/fonts` staan complete TTF-bestanden: Nunito 400, 600 en 700, samengevoegd uit de subsets met fontTools, en Grieks uit Manrope. Ze hebben nette namen en gewichten. De API geeft ze als `fontFiles` aan resvg. Er is geen woff2-decompressie meer bij het opstarten (wawoff2 is weg), en het pakket van de API neemt de map mee (`files`).
- **Controle.** `PlateImages.textWorks()` controleert of er echte letters getekend worden: "iiii", "WWWW" en een lege tekst moeten verschillende plaatjes opleveren. Zonder lettertype zijn ze gelijk (leeg), en met een verkeerd lettertype ook (blokjes).
  - De API meldt het bij het opstarten in de log als het misgaat.
  - De tests controleren Latijn, Pools en Hongaars, Cyrillisch en Grieks.

## Gevolgen
- De pins, deelplaatjes en mailplaatjes krijgen weer tekst, in alle talen.
- Een nieuw lettertype op de platen vraagt ook een TTF in deze map; de README beschrijft hoe je ze maakt.
