# 0092 · Capaciteit van de servers in het admin panel

- Status: aangenomen
- Datum: 2026-11-08

## Context
Kleurhoek draait in productie op Scaleway Serverless Containers. Website en API hebben elk 0,56 vCPU en 1 GB, en draaien altijd minstens één keer (koud starten duurt te lang). Thijs wil weten of dat kleiner kan zonder dat bezoekers het merken, en op tijd zien wanneer het juist groter moet. Tot nu toe stonden die cijfers alleen in de Scaleway-console.

## Besluit
- Nieuwe pagina **Beheer › Capaciteit** (recht `operations.capacity.read`, ook voor de rol Analist). Per container een **CapacityCard** uit het design system:
  - de maat;
  - processor en geheugen op drukke momenten;
  - een advies met de reden;
  - de vaste kosten per maand.
- Daaronder het verloop over 30 dagen en de snelheid voor bezoekers.
- **Cijfers uit Scaleway Cockpit.** De API haalt elk kwartier de metrics van vandaag en gisteren op via de Prometheus-API van Cockpit:
  - `serverless_container_cpu_usage_ratio` en `serverless_container_memory_usage_bytes`, per container op `resource_name`;
  - per dag wordt het gemiddelde en de drukste 5 % (p95) bewaard, als percentage van de maat, plus het hoogste aantal exemplaren tegelijk;
  - opslag in `operations.capacity_daily`, één rij per dag en container.
- **Snelheid zoals een bezoeker die ziet.** Elk kwartier vraagt de API een paar pagina's op via Cloudflare (`CAPACITY_SPEED_PATHS`, standaard `/` en `/platen/sinterklaas`) en meet de tijd tot het eerste antwoord. De metingen staan in `operations.speed_samples` en blijven 35 dagen bewaard. Ze tellen niet mee in analytics, omdat die alleen meet wat een browser meldt.
- **Advies, met snelheid voorop.** Het advies kijkt naar de laatste zeven dagen:
  - **groter maken** als het geheugen of de processor boven 80 % kwam, of als het maximum aantal exemplaren is bereikt;
  - **kan kleiner** pas na zeven volle dagen onder 30 % processor en 50 % geheugen, met niet meer exemplaren dan het minimum, en alleen als de site snel is (traagste 5 % onder 1,5 s);
  - anders **past**;
  - met minder dan drie dagen cijfers geeft de pagina nog geen advies.
- **Het panel adviseert alleen.** De maat staat in Terraform: `local.sizes` in `infra/modules/scaleway/apps.tf`, met de schaal per omgeving in `infra/envs/*/main.tf`. De containers en `CAPACITY_APPS` lezen allebei uit `local.sizes`, dus het panel kent altijd de echte maat. Kleiner maken doen we stap voor stap, en alleen op verzoek van Thijs.
- **Toegang tot Cockpit.** Terraform maakt een eigen Cockpit-token dat alleen metrics mag lezen (`scaleway_cockpit_token.capacity`). Het token komt als geheime variabele `COCKPIT_METRICS_TOKEN` in de API; de URL komt in `COCKPIT_METRICS_URL`. Zonder die twee meet de API alleen de snelheid, en zegt de pagina dat Cockpit nog niet gekoppeld is. Lokaal en in compose is dat de standaard.
- Kosten in de schatting: € 1,00 per 100.000 vCPU-seconden en € 0,10 per 100.000 GB-seconden (prijzen november 2026), zonder het gratis tegoed.

## Gevolgen
- Om de koppeling met Cockpit aan te zetten is een Terraform-apply in prod nodig (nieuw token, nieuwe variabelen). Dat gebeurt alleen op verzoek van Thijs.
- Na de apply eerst controleren of `resource_name` in Cockpit echt de containernaam is (`api`, `web`, `admin`, `login`). Kloppen de namen niet, dan blijven de kaarten op "Nog te weinig cijfers" staan; dat los je op in `CAPACITY_APPS`.
- Pas na een week cijfers kan de pagina "kan kleiner" adviseren.
- Een maat verkleinen blijft handwerk in Terraform. Dat is met opzet: één verkeerde knop zou de site voor alle bezoekers traag maken.
