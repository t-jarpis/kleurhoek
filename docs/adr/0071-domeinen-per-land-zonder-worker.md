# 0071 · Domeinen per land rechtstreeks naar de website, niet via de Worker

- Status: aangenomen
- Datum: 2026-11-03
- Vervangt deels: ADR 0040 (alleen de infrastructuur: de Worker voor kleurhoek.be en kleurhoek.com)

## Context
Sinds ADR 0040 liepen www/dev.kleurhoek.be en www/dev.kleurhoek.com via de Worker `kleurhoek-organisaties`. Hun DNS wees naar een leeg adres (`100::`). De Worker stuurde elk verzoek door naar de website van de omgeving en gaf de echte host mee.

Het gratis plan van Cloudflare telt 100.000 Worker-verzoeken per dag, voor het hele account. Elk verzoek telt mee: de pagina, maar ook elke plaatafbeelding, elk JS- en CSS-bestand en elke prefetch van Next.js. De beginpagina van kleurhoek.be kost zo 1 pagina plus 84 afbeeldingen en 12 bestanden. In een browser komen daar de prefetches van de links nog bij.

Zoekmachines crawlen .be en .com volledig, want elke pagina op kleurhoek.nl verwijst er via hreflang naar. Op 3 november zat het account op 75% van de daglimiet, met nauwelijks echte bezoekers. Bij de limiet geven .be en .com een foutpagina. Ook de modeltelling van Hegel Remote (hetzelfde account) valt dan stil.

## Besluit
**www/dev.kleurhoek.be en www/dev.kleurhoek.com krijgen hetzelfde als www.kleurhoek.nl:** een proxied CNAME naar de website-container van de omgeving, met een eigen domein en certificaat bij Scaleway.

- **De omgevingen zetten dit zelf** (`modules/cloudflare`: record `market`; `modules/scaleway`: `scaleway_container_domain.market`).
  - envs/zone geeft de zone-ID's per omgeving door (output `market_zones`).
  - De omgevingen lezen die uit de remote state.
- **De website ziet de echte host** in de `Host`-header en het IP-adres in `cf-connecting-ip`. Er is geen code-wijziging nodig: de proxy viel al terug op die headers.
- **Per zone (`modules/market-domain`), zoals op kleurhoek.nl:**
  - de geheime edge-header per omgeving;
  - Always Use HTTPS uit, met een eigen regel naar HTTPS die de certificaatcontrole (`/.well-known/acme-challenge/`) overslaat;
  - die controle nooit cachen;
  - dezelfde rate limit aan de rand.
- **De Worker** houdt alleen de organisatiedomeinen (`{code}.kleurhoek.nl`, `{code}-dev.kleurhoek.nl`, ADR 0017).
  - De binding `HOSTS` is leeg.
  - De code ondersteunt hem nog, voor als een vaste host ooit weer via de Worker moet.
- **`scripts/infra.sh`** controleert en herstelt de certificaten van alle eigen domeinen van de containers, ook die per land.

## Gevolgen
- Het verkeer van .be en .com (pagina's, afbeeldingen, crawlers) telt niet meer mee voor de Worker-limiet. Wat overblijft is het verkeer van organisatie-subdomeinen.
- **Overstappen:**
  - `scripts/infra.sh up dev` en daarna `scripts/infra.sh up prod`. De zone gaat eerst: die haalt de oude records en Worker-routes weg. Daarna zet elke omgeving haar eigen CNAME en domein.
  - Tussen die twee stappen, en tot Scaleway het certificaat heeft (meestal een paar minuten), zijn .be en .com van die omgeving niet bereikbaar.
  - Draai beide kort na elkaar: de zone-stap raakt ook www.kleurhoek.be en www.kleurhoek.com.
- De .be- en .com-zones hebben nu eigen regels in de fases redirect, cache, late transform en rate limit. Het API-token had die rechten al voor deze zones (infra/README.md).
- Afgewezen:
  - **Statische bestanden langs de Worker via een route-uitzondering.** Kan niet zolang de DNS naar een leeg adres wijst: zonder Worker is er geen origin.
  - **Afbeeldingen vanaf www.kleurhoek.nl laden.** Dat vraagt wijzigingen in CSP en CORS, en raakt het kleuren en exporteren op canvas. De JS-bestanden en het crawlen van pagina's zouden het toch nog kosten.
  - **Workers Paid ($5 per maand).** Blijft mogelijk, maar lost de oorzaak niet op.
