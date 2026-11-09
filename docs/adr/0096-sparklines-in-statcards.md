# 0096 · Sparklines in de StatCards

- Status: aangenomen
- Datum: 2026-11-09

## Context
De kerngetallen in het beheer (dashboard en Analytics) tonen een totaal en de verandering ten opzichte van de vorige periode, maar niet hoe het getal binnen de periode verliep. Thijs wil in het kaartje zelf zien of een week gelijkmatig was of door één dag gedragen werd.

## Besluit
- De `StatCard` krijgt een optionele `trend` (reeks per dag, per week vanaf 90 dagen) en tekent vanaf twee punten een sparkline onder de trend: alleen de vorm, y van 0 tot het hoogste punt, altijd `chart-1`, geen assen (design system: StatCard › Sparkline).
- `GET /v1/admin/analytics/overview` levert in `series` per periode ook `prints`, `pdfDownloads`, `colored`, `completions`, `shares`, `materialsViews` en `productClicks`, naast de bestaande velden. `downloads` blijft downloads + prints, zodat bestaande grafieken niet veranderen.
- Verhoudingen en getallen zonder reeks (zoals pagina's per bezoeker) krijgen geen sparkline.

## Gevolgen
- Geen nieuwe tabellen of telling: de reeksen komen uit dezelfde `daily_totals` als de totalen.
- Voor exacte waarden per dag blijft de grote grafiek onder de kaartjes.
