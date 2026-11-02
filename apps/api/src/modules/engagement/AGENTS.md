# Betrokkenheid (`engagement`)

Favorieten per account (zonder account blijven ze op het apparaat).

Besluiten: ADR 0039. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `engagement`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `engagement.module.ts` (gebruikt door: AppModule)

## Endpoints
- `/v1/me/favorites`

## Events
- Reageert op `identity.account.deleted`: favorieten weg
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
