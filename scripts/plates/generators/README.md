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
