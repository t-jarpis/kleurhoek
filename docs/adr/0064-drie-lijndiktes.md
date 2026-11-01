# 0064 · Drie lijndiktes in gedetailleerde platen

- Status: aangenomen
- Datum: 2026-11-01

## Context
De platen voor 12+ hebben honderden vlakken, maar alle lijnen zijn even dik. Het onderwerp (een uil, een vos) gaat daardoor op in de achtergrond en de plaat oogt druk. In kleurboeken voor volwassenen geeft een dikkere omtrek diepte. Thijs koos na een proef met drie sterktes voor de subtiele: fijn 0,8, middel 1,15 en dik 1,7 bij de lijndikte van 12+.

Een verbeterde tekening in `catalog-data` kwam tot nu toe niet in de database: de seed voegt alleen nieuwe platen toe.

## Besluit
- **Opbouw.** De vlakken (`.r`) blijven precies hetzelfde. Erboven komt één groep `<g class="ink">` met lijnen `class="l l2"` (middel) en `class="l l3"` (dik). Ze zijn geen vlak en vangen geen klikken. Kleur-op-nummer, het Atelier, opgeslagen kleurwerk en samen kleuren werken daardoor ongewijzigd.
- **Diktes** zijn factoren op de lijndikte van de leeftijd (`--sw`), zodat de keuze dun/normaal/dik van de bezoeker blijft werken. Tokens in het design system (PlateInk): `--ink-fine` .5, `--ink-mid` .72, `--ink-bold` 1.06. Een plaat met `.ink` tekent de vlakken met de fijne lijn (`.sheet:has(.ink) .r`); zonder `.ink` verandert er niets.
- **Overal gelijk.** Site en print via `packages/theme` (CSS). De API zet in de losse SVG en de PNG's (resvg kent geen `calc()` en `:has()`) vaste getallen als de plaat `.ink` heeft. De export uit het Atelier neemt de berekende diktes over.
- **Maken.** In de generators zegt `obj("naam")` bij welk onderwerp de volgende vlakken horen en `part()` waar een nieuw deel begint (`scripts/plates/generators/ink.py`). Dik is de zichtbare omtrek van elk onderwerp, middel die van elk groot deel (vanaf 120 vierkante eenheden). De achtergrond krijgt niets extra. De lijnen komen uit de vormen van vóór het samenvoegen van snippers, dus ze zijn glad.
- **Eerste platen.** 17 figuratieve platen voor 12+ (uil, vos, hert, vis, varens, bessen, fantasiebloem, bergen, stad, zee, lappendeken, glas-in-lood, vlinder, art-deco-zon, bloemenkrans, zentangle-blad en -kat). Pure patronen (sterpatronen, waaiers, mandala's, tegels) blijven zoals ze zijn: daar is geen voor en achter. Hun vlakken zijn gecontroleerd gelijk aan de gepubliceerde versie.
- **Nieuwe versie bij een betere tekening.** De seed vergelijkt bij het starten de md5 van de huidige SVG met `catalog-data`. Is hij anders en komt de huidige versie uit `catalog-data`, dan maakt de seed versie n+1. Het adres van de SVG en PNG bevat de versie, dus het CDN toont meteen de nieuwe. Een versie uit het admin panel wordt nooit overschreven.

## Gevolgen
- Nieuwe gedetailleerde platen krijgen de lijndiktes vanzelf zodra de generator `obj`/`part` gebruikt.
- Wie een plaat in `catalog-data` aanpast, ziet dat na de volgende uitrol op de site, ook als het aantal vlakken verandert (aangepast op 1 november, ADR 0065): opgeslagen kleurwerk hoort bij een versie en blijft bij de oude versie.
- Pinterest-plaatjes (`/v1/pins/…`) hebben geen versie in het adres en volgen binnen een week (cache).
