# 0043 · Productie schaalt niet meer naar nul

- Status: aangenomen
- Datum: 2026-10-25
- Wijzigt: ADR 0021 (API en website naar nul zolang het rustig is)

## Context
In productie schaalden API en website naar nul zolang het rustig was. De eerste bezoeker na een stille periode wachtte dan te lang: de container moet starten, de API migreert en vult de catalogus aan. Nu er bezoekers komen (ook via kleurhoek.be en .com en zoekmachines), weegt die wachttijd zwaarder dan de kosten.

## Besluit
- **Productie:** altijd minstens één API en één website (`api_min = 1`, `web_min = 1`). Dat kost ongeveer € 30 per maand extra. Het maximum blijft 6 API's en 10 websites.
- **Dev:** schaalt wel naar nul. Daar kijkt bijna niemand, en een paar seconden wachten is geen probleem.
- **Admin panel en inlogpagina** mogen in beide omgevingen naar nul. Alleen wij gebruiken het admin panel, en inloggen is zeldzaam.

## Gevolgen
- Van kracht na `scripts/infra.sh up prod`.
- De dagtotalen van analytics worden nu ook zonder koude start gewoon elke 10 minuten bijgewerkt.
