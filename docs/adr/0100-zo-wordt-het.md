# 0100 · Resultaatplaatje "Zo wordt het" bij bouwplaten

- Status: aangenomen
- Datum: 2026-11-12

## Context
Bij een bouwplaat zie je op het vel alleen de uitslag. Ouders willen vóór het printen weten wat het kind gaat maken, en een kind wil tijdens het knippen en vouwen kunnen kijken hoe het moet worden. Het ingekleurde voorbeeld (ADR 0089) laat de uitslag in kleur zien, niet het werkstuk.

## Besluit
- **Eén bron: het vel zelf.** Het plaatje staat als geneste `<svg class="kh-result">` (eigen viewBox) in een vel van de plaat, in een groep `<g class="kh-result-box">` met een dun grijs kader en het label "Zo wordt het". Het staat op het vel, wordt het label vertaald via de woordenlijst (ADR 0029; de tekst bestond al voor de pixelplaten) en krijgt een plaat met een plaatje vanzelf een nieuwe versie (ADR 0064). Geen nieuw veld in de database of de API.
- **Geen kleurvlak.** In het plaatje is elk vlak een lijn (`class="l"`) met een vaste vulkleur uit `colors.json` (de kleuren van kleur-op-nummer); er staat geen `class="r"` in, dus het telt niet mee in de vlakken, kleur-op-nummer, online kleuren of het Atelier. Huid van Piet: licht (oranje flink naar wit), alleen in het plaatje.
- **Generator-hulp `scripts/plates/generators/result.py`.** Parallelle projectie in een eenvoudig 3/4-aanzicht (`Camera`), `solid()` tekent de zichtbare vlakken van een convex model met dezelfde tekenfunctie als de uitslag (affiene afbeelding per vlak), zodat de versiering altijd klopt; `flat()` voor platte onderdelen (Piet achter de schoorsteen), `poly()` voor vrije vormen (de band van de schoen). `place_result(sh, kader, build)` past het plaatje in een kader van minstens 44 mm breed (ruimte voor een langere vertaling), lijndikte 1,2 zoals op de plaat.
- **Eerst vier platen:** `schoen-om-te-zetten` (op vel 2; stroken 2 en 3 schuiven naar links), `bouwplaat-pakjesboot` (romp 12 mm naar links, zelfde uitslag), `surprise-schoorsteendoosje` en `surprise-mijterdoosje` (`bouwplaat(..., result=(kader, build))` in batch37v). Alle vier passen op een vel; een plaat waar het niet past krijgt (nog) geen plaatje.
- **Controle.** `check.mjs` faalt als iets van de uitslag onder het kader ligt of als er een kleurvlak in het plaatje staat.
- **Website.** `lib/result.ts` haalt het plaatje uit vel 1 of een extra vel als losse SVG met `role="img"` en een alt-tekst per taal (`resultTitle`, `resultAlt` in alle 29 talen). DS-component **ResultPicture**: in Voor ouders naast de stappen (`.kh-howto`), op een smal scherm eronder. Alleen als de plaat een plaatje heeft.

## Gevolgen
- Een bouwplaat erbij: in de generator een `build(rs, s)` schrijven en `place_result` aanroepen op een vrije plek; daarna ingest met `--vervang` en de vertalingen terugzetten (zie generators/README.md).
- In de kleurstudio staat het plaatje ook op het vel (niet aan te tikken). Met "geen lijnen" in het Atelier verdwijnen ook de lijnen van het plaatje.
- Een plaatje dat op geen enkel vel past, kan nu niet alleen op de site; dan is een eigen veld of bestand nodig (nog niet gebouwd).

## Aanvulling 12 november 2026: printen optioneel
Op de website is het plaatje genoeg; op papier is het vaak overbodig. Daarom print het niet meer standaard: in de kleurstudio staat bij een plaat met een resultaatplaatje het vinkje "Ook het plaatje van het eindresultaat printen" (standaard uit). Aangevinkt zet het `data-print-result` op `<html>`; `globals.css` verbergt `.kh-result-box` in print zolang dat er niet staat. Dat geldt ook voor het printen van een los vel (ExtraPages) en het boekje. De plek op het vel blijft gereserveerd, zodat de uitslag en de nummering niet veranderen.
