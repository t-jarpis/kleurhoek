# 0073 · Wanneer wordt er gedownload en geprint

- Status: aangenomen
- Datum: 2026-11-03

## Context
Thijs wil in het admin panel zien op welk tijdstip er gedownload wordt, om te zien wanneer er activiteit is. De dagtotalen (ADR 0020) kennen alleen de dag. De ruwe events hebben wel een tijdstip en blijven 90 dagen bewaard (ADR 0002).

## Besluit
- **Endpoint** `GET /v1/admin/analytics/activity?from&to` (recht `analytics.read`). Het telt downloads en prints uit de ruwe events en geeft twee dingen terug:
  - aantallen per weekdag en uur in Nederlandse tijd;
  - de laatste 30 met tijdstip, soort, plaat, markt en apparaat.
- **Periode:** hooguit de laatste 90 dagen. Is de gekozen periode langer, dan zegt het admin panel vanaf welke datum het telt.
- **Admin panel:** Analytics › Inhoud krijgt een warmtekaart per weekdag en uur (design system: ActivityHeatmap) en de tabel Laatste downloads en prints.
- **Geen nieuwe gegevens:** we bewaren niets extra's en tonen geen bezoeker, alleen aantallen en losse handelingen zonder wie.

## Gevolgen
- Wil je dit ooit over meer dan 90 dagen zien, dan moet er een dagtabel per uur bij komen. Dat doen we pas als het nodig is.
