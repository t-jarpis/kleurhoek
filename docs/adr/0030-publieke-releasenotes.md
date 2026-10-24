# 0030 · Publieke releasenotes, voorlopig alleen in het admin panel

- Status: aangenomen
- Datum: 2026-10-24

## Context
De releasenotes in het admin panel (ADR 0023) zijn voor ons: ze noemen ook technische wijzigingen en interne onderdelen. Voor bezoekers willen we een eigen, eenvoudige tekst per wijziging, zodat we later een pagina "Wat is er nieuw" kunnen tonen.

## Besluit
- **Tweede trailer**: een commit die bezoekers merken, krijgt naast `Release-note:` ook `Public-note: <één zin voor bezoekers, in het Nederlands>`. Gewone taal, geen interne namen (geen "API", "admin", "seed").
- De Deploy-workflow neemt die trailer mee in `release-log.json`; de API bewaart hem in de releasenotes als `public`.
- **Voorlopig alleen in het admin panel**: op de pagina Releases staat per uitrol een blok "Voor bezoekers" met deze teksten. Ze staan nog niet op de website; dat besluit de eigenaar later.
- De technische notes blijven zoals ze zijn.

## Later
- Een pagina "Wat is er nieuw" op de website, per omgeving, met vertalingen per taal (Lokalisatie, sleutel `release:<sha>`).

## Gevolgen
- Geen databasewijziging: `public` is een extra veld in de bestaande JSON van de releasenotes.
- Oudere commits hebben geen publieke tekst; het blok vult zich vanaf nu.
