# 0060 · Samen kleuren op twee schermen

- Status: aangenomen
- Datum: 2026-10-30

## Context
Twee mensen op afstand, zoals een opa en een kleinkind, willen tegelijk dezelfde plaat kleuren. Dat moet kunnen zonder account en zonder dat we iets bewaren wat niet nodig is (ADR 0002).

## Besluit
- **Nieuw domein Samen kleuren** (`apps/api/src/modules/together`, schema `together`) met drie tabellen:
  - kamers: een code van vier letters (zonder I en O), plaat en versie, en het laatste moment van activiteit;
  - handelingen: in volgorde;
  - aanwezigheid: een willekeurige code per tabblad.

  Er worden geen namen, accounts of IP-adressen opgeslagen. Het domein kent de platen niet.
- **Handelingen.** Alleen vullen, een streek (dezelfde als in het Atelier, ADR 0056), iets ongedaan maken (`x`) of opnieuw beginnen (`c`). De API controleert ze streng met zod, en een kamer heeft hooguit 5000 handelingen.
  - Elk apparaat bouwt de plaat zelf op uit de lijst (`deriveShared`).
  - Eigen handelingen zijn direct zichtbaar en worden in kleine groepen verstuurd.
  - Ongedaan maken gaat alleen over je eigen handelingen.
- **Verbinding.** Long polling: een verzoek wacht tot er iets nieuws is, of hooguit 20 seconden.
  - Dat werkt met de serverless containers van Scaleway en achter Cloudflare, zonder blijvende verbinding.
  - Het werkt met meerdere replica's, omdat alles in Postgres staat.
- **Wanneer een kamer stopt.** Niet na een vaste tijd: een kamer blijft bestaan zolang iemand meedoet. Is er 30 minuten niemand meer, dan ruimt een taak de kamer op, met alles erin. Het werk blijft op elk apparaat staan.
- **Bereikbaarheid.** De website geeft alleen de vier nodige adressen door (`/v1/together/rooms…`). POST mag alleen van de eigen pagina's (same-origin).
- **Rate limits.** `together-create` (30 per uur) en `together` (1200 per minuut) per IP-adres.
- **Pagina's.** `/samen` om een code in te vullen, en `/samen/<code>` als deellink. Die stuurt door naar de plaat met `?samen=CODE`.
- **Design system.** Nieuwe component TogetherPanel en icoon `together`.

## Gevolgen
- Een nieuwe kleurhandeling in het Atelier moet ook in de lijst van toegestane handelingen van de API.
- Bij veel gelijktijdige kamers kan het wachten later naar Postgres LISTEN/NOTIFY of een eigen dienst. Het contract met de website blijft dan hetzelfde.
