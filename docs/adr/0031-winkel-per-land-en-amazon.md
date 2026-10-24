# 0031 · Winkel per land: Amazon-winkels, productlijst en aanbod per land

- Status: aangenomen
- Datum: 2026-10-24

## Context
Met meer talen en landen (ADR 0029) moet elk land eigen productlinks krijgen. Amazon heeft per land een eigen winkel en partnerprogramma. Producten één voor één met de hand invoeren per land was traag, en in het admin panel was niet te zien welk land welk product krijgt. Ook stempels moesten als materiaal met producten kunnen.

## Besluit
- **Amazon-winkels** als vaste lijst in `shop.defaults.ts` (`AMAZON_STORES`): Amazon.nl, .com.be, .de, .fr, .it, .es, .pl, .se en .co.uk, elk met de markten die ze bedienen (bijvoorbeeld Amazon.de voor de-DE, de-AT, de-CH, de-LU). Elke winkel is een partner die uit staat tot de tracking-ID is ingevuld.
- **Snel toevoegen via Amazon**: een link (ook een korte deellink, die gevolgd wordt) of een ASIN, een naam, materialen en winkels. Per winkel komt er een gewoon product (`<naam>-<winkel>`) met `https://<winkel>/dp/<ASIN>` en de markten van die winkel. Namen per taal zijn optioneel; anders de Nederlandse. Het admin panel toont daarna per winkel de link om te controleren of het product daar bestaat. Endpoint: `POST /v1/admin/shop/products/amazon`.
- **Productlijst**: alle producten met aan/uit (Switch, `PUT /v1/admin/shop/products/<slug>/enabled`), landen, materialen en een filter per land en "alleen verborgen" in de URL.
- **Per land**: een matrix met per materiaal en markt het product dat bezoekers zien, met dezelfde regel als de website (aan, partner aan, in die markt, laagste voorkeur). "Geen" laat zien waar nog iets ontbreekt.
- **Landen per product** kies je met vinkjes in plaats van een vrij tekstveld.
- **Stempels**: nieuw materiaal `stempels` (stempels en inktkussen), met eigen tekening.
- Nieuwe componenten eerst in het design system: ProductList, Switch, CoverageMatrix, AmazonQuickAdd, en FilterChip als link.

## Gevolgen
- Geen databasewijziging: dezelfde tabellen voor partners, producten en koppelingen; nieuwe partners en het nieuwe materiaal komen via de seed.
- Zonder Amazon-API (PA-API of Creators API) halen we geen titel, foto of prijs op. Dat kan later achter hetzelfde formulier, zodra er toegang is.
- Of een ASIN in een andere Amazon-winkel bestaat, controleert de beheerder met de getoonde links.
