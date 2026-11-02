# Identiteit (`identity`)

Gebruikers (leden en beheerders), rollen en permissies, het auditlog en ongedaan maken. Zitadel is de bron voor wie iemand is.

Besluiten: ADR 0007, 0042, 0066. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `identity`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `admin.guard.ts` (gebruikt door: analytics, catalog, contact, messaging, operations, organizations, shop, social, sources, storefront)
- `audit.service.ts` (gebruikt door: analytics, contact, operations, organizations, shop, social, sources)
- `identity.module.ts` (gebruikt door: AppModule)
- `identity.service.ts` (gebruikt door: messaging, organizations)
- `member.guard.ts` (gebruikt door: engagement, messaging, organizations)
- `undo.ts` (gebruikt door: analytics, operations, organizations, shop, social)

## Endpoints
- `/v1/admin`
- `/v1/admin/changes`
- `/v1/me`

## Events
- Stuurt `identity.account.deleted` (strict: als een domein faalt, mislukt het verwijderen)
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
