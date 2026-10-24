# 0027 Meer soorten werkjes: van kleurplaten naar een creatieve printbibliotheek

Datum: 24-10-2026. Status: aangenomen.

## Context
De contentopdracht van 24-10-2026 breidt Kleurhoek uit van kleurplaten naar alles wat je met een printer, papier, schaar, lijm en potloden maakt: vouwen, werkbladen, sjablonen, kaarten, tekenlessen, spellen en projecten van meerdere pagina's, voor peuters tot volwassenen. Doel: 5.000 goedgekeurde werkjes (2.000 kleurplaten, 750 knip- en knutselbladen, 500 vouw- en bouwplaten, 400 teken- en schilderactiviteiten, 600 educatieve printables en spellen, 400 kaarten en decoraties, 350 voor gevorderden). De site kende vier soorten, geen moeilijkheidsgraad en één pagina per werkje.

## Besluit
- **Soorten**: naast kleurplaat, knipplaat, bouwplaat en spel nu ook **vouwblad**, **werkblad**, **sjabloon**, **kaart** en **tekenles**. Het filter Soort op de site groepeert ze: Kleurplaten · Knutselen (knip, bouw, vouw, kaart) · Leren en spelen (werkblad, spel) · Tekenen (tekenles, sjabloon). Een groep zonder werkjes verschijnt niet.
- **Moeilijkheid** 1–3 (makkelijk, gemiddeld, uitdagend), los van de leeftijd; in het ouderdeel (DifficultyMeter).
- **Extra pagina's** per plaatversie (`plate_versions.pages`): een extra vel (onderdelen, stappen) of een **antwoordblad**. Bestanden `plates/<slug>.p2.svg` …, titels in de vertaling (`pageTitles`). In het ouderdeel met een printknop per vel; antwoorden ingeklapt (ExtraPages).
- **Leeftijd 12+** voor tieners, volwassenen en gevorderde knutselaars (data, geen code).
- **Regels per soort** (catalogustest en `scripts/plates/ingest.mjs`): knip-, bouw-, sjabloon- en kaartbladen hebben kniplijnen; vouwbladen vouwlijnen; elk werkje behalve een kleurplaat heeft stappen en materialen.
- **Kwaliteitscontrole** `scripts/plates/check.mjs`: dubbele tekeningen, ontbrekende gegevens, onderdelen buiten het vel (in een echte browser gemeten), onleesbaar kleine tekst, werkbladen met een opgave maar zonder antwoordblad. `--report` schrijft de voortgang naar `docs/content/voortgang.md`. Een werkje komt alleen in `catalog-data` als ingest en check slagen en het contactvel (preview) is bekeken.
- **Herkomst en licentie**: alle werkjes zijn eigen tekeningen, als SVG-code gemaakt; geen beeldgenerator, geen bestaande personages, merken of bouwplaten. Ze zijn van Kleurhoek (ADR 0004). Dat geldt voor de hele catalogus en staat daarom hier, niet per werkje.
- **Status**: wat in `catalog-data` staat is goedgekeurd en wordt gepubliceerd bij de volgende start (seed, ADR 0021); op productie pas na de aparte uitrol (ADR 0019).

## Gevolgen
- De site verandert licht: filter, labels, het ouderdeel en printen per vel. PDF's maken we niet apart: printen gaat via de browser (A4), net als bij kleurplaten.
- Organisaties kiezen nog steeds tussen kleurplaten en knutselen; alle nieuwe soorten vallen onder knutselen.
- 5.000 werkjes is veel werk: in batches van 25–50, met de voortgang in `docs/content/voortgang.md`.
