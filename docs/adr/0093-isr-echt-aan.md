# 0093 · Pagina's echt bewaren (ISR)

- Status: aangenomen
- Datum: 2026-11-08
- Vult aan: ADR 0006

## Context
ADR 0006 gaat ervan uit dat pagina's bij het eerste verzoek worden gemaakt en daarna bewaard (ISR). Dat gebeurde niet. In de App Router is een route met dynamische segmenten (`[org]/[market]`) zonder `generateStaticParams` altijd dynamisch. `export const revalidate` gold daardoor alleen voor de data-cache van `fetch`. Elke pagina en elke prefetch werd bij elk verzoek opnieuw gemaakt, met `Cache-Control: private, no-store`. Dat kost processortijd in de website-container, en daardoor kan die niet kleiner (ADR 0092).

## Besluit
- `generateStaticParams() { return []; }` in de layout `[org]/[market]` en in elke pagina met een eigen `[slug]`. Een lege lijst betekent dat er bij de build niets wordt gemaakt, zodat de build niet van de API afhangt. Na het eerste verzoek bewaart Next de pagina.
- Pagina's die de link lezen of persoonlijk zijn, krijgen `export const dynamic = "force-dynamic"`. Dat zijn boekje, contact, mail, mail/bevestigen, samen, account, beheer en eigen-omgeving. Anders geeft Next op de server een fout (`DYNAMIC_SERVER_USAGE`), of bewaart hij een pagina die bij één bezoeker hoort. Geen `force-static` in de layout: dan zien die pagina's lege `searchParams`.
- Nieuwe pagina's onder `[org]/[market]` die `searchParams`, `cookies()` of `headers()` gebruiken, krijgen ook `force-dynamic`.
- `expireTime: 86400`: een bewaarde pagina wordt hoogstens een dag oud uitgegeven, ook als er lang geen verzoek kwam.
- Next stuurt nu `s-maxage=30, stale-while-revalidate=86370`. De 30 seconden komen van `getOrg` in de layout (`revalidate: 30`), want de laagste revalidate van een route telt. Een wijziging in het admin panel staat dus binnen een halve minuut op de site.
- De proxy (`src/proxy.ts`) draait nog steeds bij elk verzoek, vóór de cache. IP-afscherming, pauze en doorsturen op taal of land blijven dus werken.

## Gevolgen
- Minder rekenwerk per bezoek: alleen het eerste verzoek per pagina, per container en per halve minuut maakt de pagina opnieuw.
- Elke container heeft een eigen cache. Na een uitrol begint die leeg.
- Cloudflare cachet nog geen HTML. Dat is de volgende stap, alleen op verzoek van Thijs. Dan moet een uitrol ook de Cloudflare-cache legen, en moeten de snelheidsmeting en de Uptime-check langs de cache.
- Een 404 wordt ook een halve minuut bewaard. Een net gepubliceerde plaat kan dus tot 30 seconden een 404 geven als iemand de pagina vlak ervoor opvroeg.
