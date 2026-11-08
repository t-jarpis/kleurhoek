# Beheer (`operations`)

Rate limits, toegang tot dev (IP-lijst) en releasenotes.

Besluiten: ADR 0005, 0015, 0023, 0030. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `operations`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `operations.module.ts` (gebruikt door: AppModule)
- `rate-limit.guard.ts` (gebruikt door: analytics, catalog, contact, health, identity, messaging, organizations, shop, sources, storefront, together)
- `site-access.service.ts` (gebruikt door: organizations)

## Endpoints
- `/v1/admin/capacity`
- `/v1/admin/rate-limits`
- `/v1/admin/releases`
- `/v1/admin/site-access`
- `/v1/internal/site-access`
- `/v1/news`

## Events
- Nog geen.
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
