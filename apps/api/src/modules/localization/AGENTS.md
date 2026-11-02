# Vertaling (`localization`)

Markten, talen en vertalingen van teksten, inclusief de woordenlijsten van de tekstlaag in platen.

Besluiten: ADR 0029, 0040. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `localization`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `localization.module.ts` (gebruikt door: catalog, messaging, organizations, shop, sources, storefront)
- `localization.service.ts` (gebruikt door: catalog, messaging, organizations, shop, sources, storefront)

## Endpoints
- Geen.

## Events
- Nog geen. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
