# Social (`social`)

Voorstellen voor Pinterest, Facebook en Instagram, goedkeuren en plaatsen via de officiële API's.

Besluiten: ADR 0063. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `social`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `social.module.ts` (gebruikt door: AppModule)

## Endpoints
- `/v1/admin/social`

## Events
- Nog geen. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
