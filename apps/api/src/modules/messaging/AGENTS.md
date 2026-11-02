# Berichten (`messaging`)

Mail: abonnees, templates, workflows, campagnes, wachtrij en bezorging. Geen tracking.

Besluiten: ADR 0037, 0038. Grenzen tussen domeinen: ADR 0001.

## Data
- Schema: `messaging`. Alleen dit domein leest en schrijft deze tabellen (row-level security per tenant via `withTenant`).

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.

- `mailer.ts` (gebruikt door: social)
- `messaging.module.ts` (gebruikt door: social)

## Endpoints
- `/v1/admin/mail`
- `/v1/mail`
- `/v1/mail/events`
- `/v1/me/mail`

## Events
- Reageert op `identity.account.deleted`: het mailabonnement van die gebruiker weg
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
