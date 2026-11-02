# Beschikbaarheid (`availability`)

Feestdagen, seizoenen en datums per land: welke platen nu in het seizoen zijn en wanneer een feest is.

Besluiten: ADR 0003, 0054. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `availability`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `availability.module.ts` (gebruikt door: storefront)
- `availability.service.ts` (gebruikt door: storefront)

## Endpoints
- Geen.

## Events
- Nog geen. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
