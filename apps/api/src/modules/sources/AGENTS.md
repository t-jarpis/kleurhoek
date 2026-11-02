# Bronnen (`sources`)

Bronnengids: thema's met goedgekeurde externe bronnen en controle of ze nog werken.

Besluiten: ADR 0025. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `sources`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `sources.module.ts` (gebruikt door: storefront)
- `sources.service.ts` (gebruikt door: storefront)

## Endpoints
- `/v1/admin/sources`

## Events
- Nog geen.
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
