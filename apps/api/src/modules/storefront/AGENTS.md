# Etalage (`storefront`)

Wat de site te zien krijgt: platen per markt en organisatie, SVG en PNG (resvg), pins en deelplaatjes. Leest alleen via de services van andere domeinen.

Besluiten: ADR 0055, 0057, 0062, 0064. Grenzen tussen domeinen: ADR 0001.

## Data
- Geen eigen tabellen.

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `storefront.module.ts` (gebruikt door: messaging, social)
- `storefront.service.ts` (gebruikt door: messaging, social)

## Endpoints
- `/v1`
- `/v1/admin/seo`

## Events
- Nog geen.
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
