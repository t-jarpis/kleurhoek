# 0097 · Wanneer er online gekleurd en getekend wordt

- Status: aangenomen
- Datum: 2026-11-09

## Context
Analytics › Inhoud laat per weekdag en uur zien wanneer er gedownload en geprint wordt, met de laatste 30 keer (ADR 0073, 0083). Voor online kleuren en tekenen in de kleurstudio was er alleen een totaal. Thijs wil die ook als lijst zien.

## Besluit
- `GET /v1/admin/analytics/activity` krijgt `kind=use|colored` (standaard `use`). `colored` telt `plate_colored` (begonnen met kleuren of tekenen op een plaat) en `plate_completed` (kleur op nummer af), uit dezelfde ruwe events, met dezelfde heatmap, de laatste 30 en "kwam binnen via".
- Analytics › Inhoud toont het als tweede blok onder de downloads en prints, met dezelfde componenten (ActivityHeatmap, tabel).

## Gevolgen
- Geen nieuwe events of tabellen. "Begonnen" telt per keer dat iemand op een plaat begint, niet per bezoek.
