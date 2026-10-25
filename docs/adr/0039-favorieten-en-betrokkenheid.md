# 0039 · Favorieten en het domein Betrokkenheid

- Status: aangenomen
- Datum: 2026-10-25

## Context
Kleuren en printen kan zonder account, en dat blijft zo (ADR 0002). Een account moet dan wel iets toevoegen. Tot nu toe gaf het alleen mailvoorkeuren. Het eerste wat ouders en leerkrachten willen bewaren zijn platen die ze nog eens willen gebruiken.

## Besluit
- **Domein Betrokkenheid** (`apps/api/src/modules/engagement`, schema `engagement`), eerder gepland voor fase 2, begint nu met **favorieten**: per account welke platen, op volgorde van toevoegen, hooguit 500. Alleen platen die bestaan. Geen gedrag, geen tijden van bekijken.
- **Zonder account op het apparaat**, met account **op elk apparaat**. De site bewaart favorieten in de browser. Na inloggen worden ze één keer samengevoegd met het account; daarna is het account leidend, zodat iets wat op een ander apparaat is weggehaald niet terugkomt. Elke wijziging gaat via de eigen `/auth/favorites`-routes naar `/v1/me/favorites`; het token komt niet in de browser.
- **Op de site**: een hartje met tekst (Bewaar / Favoriet) in de kleurstudio (design system: FavoriteButton) en de chip Favorieten in het filter Onderwerp zodra er favorieten zijn. Na de eerste favoriet zonder account staat er eenmalig een hint dat inloggen ze op al je apparaten bewaart. Op de accountpagina staat wat een account je geeft (AccountBenefits).
- Een verwijderd account neemt zijn favorieten mee.
- Volgende kandidaten voor dit domein (nog niet gebouwd): boekjes bewaren, kleurwerk van de koelkast bewaren, en profielen per kind onder het account van de ouder (alleen een bijnaam en leeftijdsgroep).

## Gevolgen
- Migratie 0024: schema `engagement` met `favorites`, met RLS.
- De privacytekst noemt wat een account bewaart: naam, e-mailadres en favorieten.
