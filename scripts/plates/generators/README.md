# Generators voor werkjes

Elk werkje is een eigen tekening, gemaakt als SVG-code (ADR 0027). Deze scripts maken de concepten van een batch opnieuw; daarna gaan ze door `ingest.mjs` en `check.mjs`.

```sh
cd scripts/plates/generators
OUT=/tmp/batch1 python3 batch1_werkbladen.py   # en batch1_teken.py, batch1_kaart.py, batch1_overig.py
node ../preview.mjs /tmp/batch1 /tmp/batch1.png   # contactvel bekijken
node ../ingest.mjs /tmp/batch1                    # toevoegen aan packages/catalog-data
node ../check.mjs --report                        # hele catalogus controleren, voortgang bijwerken
```

`kit.py` bevat de bouwstenen: vlakken (`r`, om in te kleuren), lijnen (`l`), knippen (`cut`), vouwen (`fold`), lijmen (`glue`), tekst (`tx`) en extra pagina's.
