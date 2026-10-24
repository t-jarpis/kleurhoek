# 0021 Productie: klein starten, catalogus bij elke start

Datum: 24-10-2026. Status: aangenomen.

## Context
Productie stond klaar met een zware database (DB-PRO2-XXS met HA, circa € 125 per maand) en zonder seed bij het opstarten. Een nieuwe site heeft nog weinig bezoekers, en zonder seed blijft de catalogus in productie leeg; nieuwe platen uit `@kleurhoek/catalog-data` zouden er nooit komen.

## Besluit
- Productie start met DB-PLAY2-PICO (één node, 10 GB, dagelijkse back-up 35 dagen in een ander datacenter), circa € 20 per maand. Groeien is één regel in `infra/envs/prod/main.tf` (`node_type`, eventueel `ha = true`).
- De API draait ook in productie bij elke start de seed. Die is aanvullend: wat in het admin panel is aangepast blijft staan.
- API en website schalen ook in productie naar nul zolang het rustig is (circa € 30 per maand minder). Na een stille periode wacht de eerste bezoeker enkele seconden. Met dagelijks verkeer gaan `api_min` en `web_min` naar 1.
- Omdat de API dan soms niet draait, telt hij bij het opstarten en daarna elke 10 minuten alle dagen op die achterlopen (niet alleen vandaag en gisteren); er gaan geen bezoeken verloren.
- `scripts/infra.sh up prod` maakt het Scaleway-project aan, zet alles op en zet daarna kleurhoek.nl, kleurhoek.be en kleurhoek.com live als doorstuur naar www.

## Gevolgen
- Zonder tweede node is er bij een storing van de database een korte onderbreking; de back-ups staan in een ander datacenter.
- Dev en prod delen geen data: producten, partners, organisaties en materialen bij platen die in het admin panel van dev zijn gezet, moeten in productie opnieuw (de voorgestelde producten maken dat twee klikken).
