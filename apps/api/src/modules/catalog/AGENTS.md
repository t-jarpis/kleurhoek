# Catalogus (`catalog`)

Platen en hun versies (SVG, vlakken, kleur-op-nummer), leeftijden, onderwerpen, materialen en collecties. De bron is `@kleurhoek/catalog-data`; de seed vult aan.

Besluiten: ADR 0027, 0036, 0064. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `catalog`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `catalog.module.ts` (gebruikt door: analytics, engagement, messaging, organizations, shop, storefront)
- `catalog.service.ts` (gebruikt door: analytics, engagement, messaging, organizations, shop, storefront)

## Endpoints
- `/v1/admin/collections`

## Events
- Nog geen. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
