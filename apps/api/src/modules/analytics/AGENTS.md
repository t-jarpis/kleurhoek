# Analytics (`analytics`)

Eigen telling zonder cookies: events ontvangen, per dag samenvatten (bezoeken, platen, bronnen, apparaten), doelen en zoekcijfers van Google en Bing.

Besluiten: ADR 0002, 0020, 0022, 0032, 0034, 0041, 0084. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `analytics`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `analytics.module.ts` (gebruikt door: AppModule)

## Endpoints
- `/v1/admin/analytics`
- `/v1/internal/events`
- `/v1/internal/wishes`

## Events
- Nog geen.
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
