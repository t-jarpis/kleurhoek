# 0046 · Tien nieuwe markten: Duits, Frans, Engels, Spaans, Italiaans en Pools

- Status: aangenomen
- Datum: 2026-10-25

## Context
Na Nederland, België en het Verenigd Koninkrijk (ADR 0040, 0044) komen er bezoekers uit Duitsland, Zwitserland, Frankrijk, Polen, de VS en andere landen. De websiteteksten bestonden al in zeven talen. De platen waren vertaald in het Duits, Frans en Engels; Spaans, Italiaans en Pools nog niet.

## Besluit
- **Nieuwe markten op kleurhoek.com**, elk op `/<markt>`:
  - Duits: de-DE, de-AT, de-CH
  - Frans: fr-FR, fr-CH
  - Engels: en-US, en-IE
  - Spaans: es-ES
  - Italiaans: it-IT
  - Pools: pl-PL
- **Zwitserland** krijgt Duits en Frans naast elkaar, net als België.
- **Account** vanaf de leeftijd die dat land voor digitale toestemming hanteert: 13 (VS), 14 (Oostenrijk, Spanje, Italië), 15 (Frankrijk) of 16 (overige).
- **Vertaling:** alle platen die niet taalgebonden zijn, plus de woordenlijst van de teksten in platen, zijn vertaald in het Spaans, Italiaans en Pools. Het Duits is aangevuld. `check-lang.mjs` controleert per taal of alles op het vel past.
- **Papier:** in de VS en Canada wordt op Letter geprint (benoemde `@page`, `html[data-paper="letter"]`), elders op A4.
- **Kalender per land:**
  - **Nieuwe feestdagen:** Driekoningen (DE, AT, CH, FR, ES, IT, PL), St Patrick's Day (IE, VS), Independence Day en Thanksgiving (VS), 14 juillet (FR).
  - **Andere datums:**
    - Nikolaus en Mikołajki op 6 december (DE, AT, CH, PL).
    - Moederdag: laatste zondag van mei (FR), eerste zondag van mei (ES), 26 mei (PL), Mothering Sunday (IE).
    - Vaderdag: Hemelvaart (DE), tweede zondag van juni (AT), eerste zondag van juni (CH), 19 maart (ES, IT), 23 juni (PL).
    - Eerste schooldag per land.
  - **Alleen waar ze gevierd worden:**
    - Carnaval: NL, BE, DE, AT, CH, FR, ES, IT
    - Sint-Maarten: NL, BE, DE, AT, CH
    - Hemelvaart: NL, BE, DE, AT, CH, FR
    - Pinksteren: NL, BE, DE, AT, CH, FR, PL
    - Dierendag: NL, BE, DE, AT, CH, PL
  - Het seizoen herfst geldt overal.

## Gevolgen
- De websitecode bepaalt welke markten live zijn (ADR 0044). Ze komen dus live met de release; daar is geen infra-run voor nodig.
- en-US gebruikt de Britse spelling van de Engelse vertaling (colour). Aparte Amerikaanse teksten zouden een vertaallaag per markt vragen in plaats van per taal; dat is een latere stap.
