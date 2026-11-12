# Generators voor werkjes

Elk werkje is een eigen tekening, gemaakt als SVG-code (ADR 0027). Deze scripts maken de concepten van een batch opnieuw; daarna gaan ze door `ingest.mjs` en `check.mjs`.

```sh
cd scripts/plates/generators
OUT=/tmp/batch1 python3 batch1_werkbladen.py   # en batch1_teken.py, batch1_kaart.py, batch1_overig.py
node ../preview.mjs /tmp/batch1 /tmp/batch1.png   # contactvel bekijken
node ../ingest.mjs /tmp/batch1                    # toevoegen aan packages/catalog-data
node ../check.mjs --report                        # hele catalogus controleren, voortgang bijwerken
```

Batch 1 staat in `batch1_*.py`; vanaf batch 2 gebruiken de batches de herbruikbare generators in `lib_gen.py` (doolhof, verbind-de-punten, rekenblad, schrijfblad, mandala, patroon, kaart): `OUT=/tmp/batch2 python3 batch2.py`.

`kit.py` bevat de bouwstenen: vlakken (`r`, om in te kleuren), lijnen (`l`), knippen (`cut`), vouwen (`fold`), lijmen (`glue`), tekst (`tx`) en extra pagina's.

## Bouwplaten van veelvlakken (`polyhedra.py`)
Een bouwplaat wordt uitgerekend uit een 3D-model (hoekpunten en vlakken): de uitslag ontstaat door de vlakken langs een boom van gedeelde randen plat te leggen. Elk randpaar dat na het vouwen samenkomt krijgt precies één lijmflap, en shapely controleert dat vlakken en flappen niet overlappen. Zo klopt de montage altijd. Nodig: `pip install shapely` (alleen voor de generators). Modellen: prisma, piramide, afgeknotte piramide, dubbele piramide, antiprisma, en via `hull_faces` elk klein convex veelvlak (kuboctaëder, afgeknot viervlak).

## Drie lijndiktes (`ink.py`, ADR 0064)
Gedetailleerde platen (12+) krijgen een dikke omtrek per onderwerp en middellijnen per groot deel. Zet in de generator `obj("uil")` vóór de vlakken van een onderwerp en `part()` vóór elk deel (vleugel, buik, oog); de achtergrond is `obj("bg")` of de stand aan het begin. `kp12` in `batch13e.py` zet de laag er daarna vanzelf in (`<g class="ink">`). Een bestaande plaat bijwerken: genereer opnieuw, controleer dat de vlakken gelijk zijn, en vervang alleen wat ná de vlakken staat; de seed maakt er bij de volgende start een nieuwe versie van.

## Sinterklaas (`batch44_sint.py`, ADR 0065)
Figuren `sint()` (mijter, baard, mantel, staf), `piet()` (Roetveegpiet: baret met veer, kraag, pofbroek, roetvegen op de wangen) en `horse()` (het paard). `OUT=/tmp/sint python3 batch44_sint.py`; de 12+-plaat staat in `batch13e.py` (`sinterklaas-glas-in-lood`).

## Sinterklaas-knutsels (`batch47_sint.py`)
Schoen om te zetten, pakjesboot, schoorsteendoosje, vingerpoppetjes, verlanglijstje en slinger: `OUT=/tmp/sint3 python3 batch47_sint.py [slug ...]`. De schoen is een band met twee zijkanten (twee vellen): het zijprofiel is een lijn langs wreef, neus, zool en hak, de band is precies zo lang als die lijn en verdeeld in drie stroken met naden A en B. Het script controleert de lengte, de plek van de knik bij de hak en dat de neus niet scherper buigt dan de tandjes aankunnen. Let op: `ingest.mjs --vervang` zet alleen de Nederlandse teksten terug in `plates.json`; zet de vertalingen er daarna opnieuw in.

## Illustratiestijl (`illu.py`, ADR 0090)
Schattige, getekende platen: `smooth(punten)` voor vloeiende vormen met een licht trillende lijn, `O(vorm, code)` voor hoofdvormen met een inktrand die rechtsonder dikker wordt, `L2(pad)` voor penseelstreken, en onderdelen als `eye`, `leaf`, `fern`, `tuft`, `cloud`, `flower` en `scales`. `R`/`C` nemen de kleurcode mee en `codes()` geeft de reeks voor de meta. Dino's: `OUT=/tmp/illu python3 illu_dinos.py`, daarna `node ../ingest.mjs /tmp/illu`. Stijlregels: PlateIllustration in het design system.

## Lijntekening omzetten (`trace.py`, ADR 0091)
`python3 trace.py bron.png uit.svg --kier 21 --nummers vlakken.png`: lijnen worden een inktlaag, witte gebieden gesloten vlakken (kiertjes gedicht). Met `--nummers` zie je het volgnummer per vlak om de kleurcodes te kiezen. Proefplaat: `OUT=/tmp/proef python3 beeldmodel_proef.py`. Nodig: `pip install opencv-python-headless numpy`.

## Resultaatplaatje "Zo wordt het" (`result.py`, ADR 0100)
Een kleine tekening van het in elkaar gezette werkstuk in een hoek van het vel. Schrijf in de generator `build(rs, s)` (s = mm per eenheid van het model) en roep `place_result(sh, (x, y, w, h), build)` aan op een vrije plek (minstens 44 mm breed). In `build`: `solid(rs, Camera(-30, 24, s), model, codes, draw_face, offset)` voor elk convex deel (met dezelfde `draw_face` als de uitslag), `flat()` voor platte onderdelen en `poly()` voor vrije vormen. Vlakken worden vaste kleuren (geen `class="r"`), tekst valt weg. `check.mjs` meldt als het kader iets van de uitslag raakt. Daarna `ingest.mjs <map> <slug> --vervang` en de vertalingen in `plates.json` terugzetten. In batch37v: `bouwplaat(..., result=((x, y, w, h), build))`.

