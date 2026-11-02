# 0068 · Eerste domeinevents en meer ongedaan maken

- Status: aangenomen
- Datum: 2026-11-02

## Context
ADR 0066 koos voor domeinevents als richting, stap voor stap. Twee koppelingen vroegen er nu om. Identity riep bij het verwijderen van een account zelf drie andere domeinen aan. En Social moest weten welke platen nieuw zijn, zonder de catalogus van binnen te kennen. Ook ontbrak ongedaan maken nog bij Social en bij de instellingen van organisaties.

## Besluit
- **DomainEvents** (`apps/api/src/shared/events.ts`, globaal module). Typen per event in `DomainEventMap`.
  - `on(event, domein, handler)` om te luisteren, `emit(event, payload, { strict })` om te sturen.
  - Gewoon: een fout bij een luisteraar wordt gelogd en de rest gaat door.
  - `strict`: een fout bij een luisteraar laat het sturen mislukken.
  - Binnen het proces, zonder wachtrij. Een wachtrij komt pas als een luisteraar traag of onbetrouwbaar wordt.
- **`identity.account.deleted`** (strict). Berichten, Betrokkenheid en Organisaties ruimen hun gegevens van die gebruiker op. Lukt dat ergens niet, dan blijft het account bestaan en krijgt de gebruiker een fout. Zo blijft er nooit iets achter.
- **`catalog.plates.published`.** De catalogus stuurt dit na de seed bij het opstarten, met nieuwe en gewijzigde platen. Social zet nieuwe platen vooraan in de rij voor Pinterest.
- **Contract.** Het kopje Events in elke `AGENTS.md` zegt wie wat stuurt en waarop reageert. Het wordt gemaakt uit de code.
- **Ongedaan maken erbij:**
  - Social: instellingen, een kanaal aan of uit, en een post goedkeuren, afwijzen of aanpassen. Een post die al geplaatst is, kan niet terug. Ontkoppelen staat in het auditlog, maar kan niet terug, want de sleutels zijn dan weg.
  - Organisaties: instellingen van een organisatie (naam, domeinen, huisstijl, aanbod, functies; het logo blijft) en het aanbod dat een school zelf instelt.

## Gevolgen
- Een nieuw domein dat gegevens van gebruikers bewaart, luistert naar `identity.account.deleted`. Identity hoeft daarvoor niet te veranderen.
- Social schrijft nu naar het auditlog, net als de andere domeinen.
