# Gezondheid (`health`)

`/health` voor de container en de uitrol. Geen eigen data.

Besluiten: ADR 0019, 0043. Grenzen tussen domeinen: ADR 0001.

## Data
- Geen eigen tabellen.

## Publiek
Andere domeinen importeren alleen deze bestanden. De test `test/boundaries.test.ts` controleert dat.


## Endpoints
- `/health`

## Events
- Nog geen.
- Typen staan in `src/shared/events.ts`. Nieuwe koppelingen tussen domeinen liefst als event (ADR 0066).

## Regels
- Wijzigingen door beheerders in dezelfde transactie vastleggen met `AuditService.record` (wie, wat, voor en na).
- Iets nieuws publiek maken? Zet het hierboven en houd het klein: een service-methode, geen tabel.
- Geen imports van de interne bestanden van een ander domein; vraag het aan zijn publieke service.
