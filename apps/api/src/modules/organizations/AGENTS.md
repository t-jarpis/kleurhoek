# Organisaties (`organizations`)

Organisaties met eigen site: huisstijl, domein, aanbod, functies en vindbaarheid (SEO).

Besluiten: ADR 0017, 0028, 0035, 0036, 0047. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `organizations`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `offer.ts` (gebruikt door: storefront)
- `organizations.module.ts` (gebruikt door: AppModule)
- `organizations.service.ts` (gebruikt door: catalog, identity, storefront)

## Endpoints
- `/v1`
- `/v1/admin/organizations`
- `/v1/me/organizations`

## Events
- Nog geen. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
