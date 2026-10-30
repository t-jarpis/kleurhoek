# Lettertypen voor PNG-plaatjes

Complete TTF-bestanden voor resvg (ADR 0062), samengevoegd uit de subsets in `packages/theme/fonts`:
Nunito 400, 600 en 700 (Latijn, Latijn-uitgebreid, Cyrillisch) en Manrope 400 en 700 (Grieks). Beide onder de
SIL Open Font License 1.1 (zie OFL-Nunito.txt; Manrope valt onder dezelfde licentie).

Opnieuw maken (Python met `fonttools` en `brotli`), vanuit de repo-root:

```python
from fontTools.ttLib import TTFont
from fontTools.merge import Merger
import tempfile
for w in ["400", "600", "700"]:
    parts = []
    for s in ["latin", "latin-ext", "cyrillic"]:
        f = TTFont(f"packages/theme/fonts/nunito/nunito-{s}-{w}-normal.woff2"); f.flavor = None
        p = tempfile.mktemp(suffix=".ttf"); f.save(p); parts.append(p)
    Merger().merge(parts).save(f"apps/api/fonts/nunito-{w}.ttf")
for w in ["400", "700"]:
    f = TTFont(f"packages/theme/fonts/manrope/manrope-greek-{w}-normal.woff2"); f.flavor = None
    f.save(f"apps/api/fonts/manrope-greek-{w}.ttf")
```

Zet daarna de namen goed (familie "Nunito" of "Manrope", stijl Regular, SemiBold of Bold, en het gewicht in OS/2).
`PlateImages.textWorks()` en `test/together.test.ts` controleren dat er echte letters op de plaatjes komen.
