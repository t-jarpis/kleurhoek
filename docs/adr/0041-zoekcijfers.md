# 0041 · Zoekcijfers van Google en Bing in het admin panel

- Status: aangenomen
- Datum: 2026-10-25

## Context
We willen zien hoe vaak Kleurhoek in zoekresultaten staat, hoe vaak erop geklikt wordt en op welke zoektermen. Onze eigen telling (ADR 0032) ziet alleen bezoekers die binnenkomen. Zoekmachines delen geen zoekterm meer in de verwijzer.

## Besluit
- **De API haalt de cijfers zelf op**, elke 6 uur, alleen in productie:
  - Google: Search Console API met een serviceaccount (alleen lezen, domeineigenschap `sc-domain:<domein>`).
  - Bing: Webmaster API met een API-sleutel.
  - Er zijn geen bibliotheken van de zoekmachines, alleen hun HTTP-API's.
  - De eerste keer gaat het 180 dagen terug; daarna steeds de laatste 5 dagen opnieuw, omdat de zoekmachines die nog bijstellen.
- **Opslag** in Analytics: `search_stats` per dag, zoekmachine, domein en soort. Er zijn drie soorten: totaal, zoekterm en pagina. Per regel staan klikken, vertoningen en gemiddelde positie.
  - Zeldzame zoektermen laten de zoekmachines zelf al weg; er staan geen persoonsgegevens in.
  - De stand per koppeling staat in `search_sync`.
- **Admin panel › Vindbaarheid › Zoekcijfers:**
  - klikken en vertoningen per dag;
  - CTR en positie per domein;
  - top 50 zoektermen en pagina's;
  - de eigen telling van bezoeken via zoekmachines, per zoekmachine en per domein;
  - de stand van de koppeling, met een knop "Nu ophalen".
  - Zonder sleutels staat er uitleg hoe je de koppeling instelt.
- **Sleutels:**
  - Het pad naar de JSON-sleutel van Google en de Bing-sleutel staan in `infra/envs/prod/terraform.tfvars` (blok `search`, niet in git). Terraform zet ze als geheime omgevingsvariabelen (`GOOGLE_SEARCH_KEY`, `BING_WEBMASTER_KEY`).
  - Search Console verifieert de domeinen met DNS-TXT-records (`search_verification` in envs/zone).
  - Bing kan de sites uit Search Console importeren.

## Gevolgen
- Migratie 0026: `analytics.search_stats` en `analytics.search_sync`, met RLS.
- Rechten: bekijken met `seo.read`, nu ophalen met `seo.manage`.
- Het serviceaccount in Google Cloud en de API-sleutel in Bing maakt Thijs zelf aan. Wij zetten nooit een sleutel in de repo.
