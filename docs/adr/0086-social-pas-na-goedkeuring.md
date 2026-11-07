# 0086 · Social: voorstellen en plaatsen pas na goedkeuring door het platform

- Status: aangenomen
- Datum: 2026-11-07

## Context
Pinterest is gekoppeld, maar de app heeft nog Trial-toegang. Pins die je met Trial-toegang maakt, zijn alleen voor jezelf zichtbaar (sandbox). Toch maakte Kleurhoek elke dag pin-voorstellen (ADR 0063), en wie die goedkeurde, plaatste ze onzichtbaar. Via de API is niet te zien of een app al Standard-toegang heeft. Bij Meta is het vergelijkbaar: het platform bepaalt wanneer openbaar plaatsen mag.

## Besluit
- Per kanaal is er een vlag "goedgekeurd voor openbaar plaatsen" (`live` in de instellingen van het kanaal). Standaard staat die uit, ook voor kanalen die al gekoppeld zijn.
- De beheerder zet hem aan in Social: "Goedgekeurd door Pinterest" of "Goedgekeurd door Meta". Dat komt in het auditlog en is ongedaan te maken.
- **Zolang de vlag uit staat:**
  - maakt Kleurhoek voor dat kanaal geen voorstellen;
  - wordt er niets geplaatst: goedgekeurde posts blijven staan, zonder dat er een poging telt;
  - toont het kanaal "Wacht op goedkeuring", met uitleg.
- De voorstellen "om te delen" (handmatig) gaan gewoon door.
- Meta: met Standard Access werkt een Business-app alleen voor de pagina's en accounts van mensen met een rol op de app. Dat is precies onze situatie, dus er is geen App Review nodig. De vlag geeft aan dat de koppeling getest is en openbaar mag.

## Gevolgen
- Er is geen migratie nodig: `settings` van een kanaal is al jsonb.
- Al bestaande pin-voorstellen blijven staan. Die kan de beheerder afwijzen of laten staan tot Pinterest goedkeurt.
