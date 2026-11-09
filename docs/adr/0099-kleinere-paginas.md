# 0099 · Kleinere pagina's: platenlijst los, kaarten als korte rij

- Status: aangenomen
- Datum: 2026-11-09
- Vult aan: ADR 0084 (zoeken), ADR 0093 (ISR)

## Context
De HTML van de voorpagina was ruim 400 kB, waarvan 380 kB de RSC-payload (`self.__next_f.push`). Daarin zat de hele lijst van alle 1.111 platen, omdat de voorpagina die als prop meegaf aan drie client components: `Browse` (zoeken en filters), `Fridge` (koelkast) en `Surprise` (alleen de slugs). Wat een client component als prop krijgt, staat altijd in de pagina; voor elke bezoeker, ook als die niet zoekt. Het raster zelf staat niet in de HTML: `Browse` leest `useSearchParams`, en op een bewaarde pagina (ISR) rendert Next dat pas in de browser.

Onderwerppagina's (`/onderwerp`, `/leeftijd`, `/soort`, `/feestdag`, `/werelddeel`) hadden een ander probleem: alle kaarten worden op de server gemaakt (goed voor vindbaarheid), maar elke kaart stond ook als React-boom in de payload, ruim 500 tekens per kaart. `/leeftijd/4-6` (447 kaarten) was daardoor 500 kB.

Thijs wilde snellere pagina's zonder infrastructuur te veranderen (geen Cloudflare-cache, geen Terraform).

## Besluit
- **Platenlijst als eigen adres:** `<markt>/platen.json` (route `app/[org]/[market]/platen.json/route.ts`) geeft dezelfde lijst als `api.plates` voor de organisatie en markt. Bewaard zoals de pagina's (ISR, ADR 0093): `generateStaticParams` met een lege lijst, `revalidate = 300`, dezelfde tags (`plates`, `market:…`, `org:…`), en via `getOrg` hoogstens een halve minuut oud (`s-maxage=30`). Onbekende organisatie of markt: 404. `x-robots-tag: noindex`.
- **De voorpagina laadt hem vooruit** met `preload(…, { as: "fetch", crossOrigin: "anonymous" })`, zodat hij tegelijk met de scripts binnenkomt. `Browse`, `Surprise` en `Fridge` halen hem op met `loadPlates`/`usePlates` (`lib/plate-index.ts`): één verzoek per bezoek, één nieuwe poging bij een fout.
  - `Browse` toont tot de lijst er is alleen het anker `#platen` (`aria-busy`), zodat links uit de seizoensband nog steeds naar het raster springen. Lukt het laden niet, dan blijft het daarbij: geen lege lijst, want dan zou elk zoekwoord als "gemist" naar `/w` gaan.
  - `Fridge` haalt de lijst alleen op als er iets op de koelkast hangt; `Surprise` pas bij een klik (meestal heeft het raster hem dan al).
  - Zoeken, filters, tellers, `?q=`, aanvragen en het doorgeven van gemiste woorden (ADR 0084) werken zoals eerst.
- **Kaarten als korte rij op onderwerppagina's:** de server rekent per kaart label, kleur en alt uit en geeft een rij `[slug, naam, svg, label, kleur, leeftijd, soort, alt]` aan de client component `PlateGrid` (`lib/cards.ts`). Het vaste begin van het svg-adres valt weg. `PlateGrid` maakt met `CardView` precies dezelfde HTML als `PlateCard`, dus alle kaarten en links blijven in de HTML.
- **Minder preloads op de voorpagina:** van de minikaartjes in de seizoensband laden alleen de eerste 4 meteen (`eager`), de rest lazy. React zette voor elk eager plaatje een preload in de `<head>`, vóór de CSS.
- **Bewaking:** `lib/payload.test.ts` faalt als een server component `plates` of `slugs` aan een client component geeft, controleert het vooruit laden en de ISR-instellingen van `platen.json`, en de korte rij (heen en terug gelijk, onder 120 tekens per kaart).

## Gevolgen
Lokaal gemeten (productiebuild, 1.111 platen, nl-NL), HTML ongecomprimeerd → na, gzip tussen haakjes:

| Pagina | Voor | Na |
|---|---|---|
| Voorpagina | 403 kB (54 kB) | 78 kB (15 kB) + `platen.json` 267 kB (32 kB), bewaard en vooruit geladen |
| `/leeftijd/4-6` (447 kaarten) | 498 kB (44 kB) | 276 kB (35 kB) |
| `/soort/knutselen` (303) | 383 kB (36 kB) | 219 kB (29 kB) |
| `/onderwerp/dieren` (140) | 191 kB (21 kB) | 122 kB (18 kB) |
| `/feestdag/sinterklaas` (43) | 99 kB (14 kB) | 78 kB (13 kB) |
| Plaatpagina | 76–127 kB | gelijk |

- Het raster op de voorpagina verschijnt na het ophalen van `platen.json` in plaats van direct na het laden van de scripts. Door het vooruit laden kost dat in de praktijk geen extra wachttijd; het raster stond al niet in de HTML.
- Bij een navigatie binnen de site naar de voorpagina is de RSC-payload ook 330 kB kleiner. De lijst komt dan uit het geheugen als hij al geladen was.
- `platen.json` is een extra verzoek per container en per halve minuut naar de API, net als een pagina. Cloudflare cachet het nog niet (net als de HTML, ADR 0093).
- Plaatpagina's veranderen niet: daar zitten vooral de SVG zelf en de gegevens voor de kleurstudio in, en die zijn nodig. JavaScript per pagina (ongeveer 155 kB gzip, vooral React en Next) en de lettertypen (`font-display: swap`, unicode-range) waren al in orde.
- Nieuwe lange lijsten van kaarten in een server component: `PlateGrid` met `packCard(cardOf(…))` gebruiken, niet honderden `PlateCard`'s.
