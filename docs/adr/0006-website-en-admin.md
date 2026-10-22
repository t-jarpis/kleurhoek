# 0006 · Website en admin panel in Next.js

- Status: aangenomen
- Datum: 2026-10-22

## Besluit
- **Website (`apps/web`)**: Next.js 16 (App Router). Markt in de URL (`/nl-nl`); `/` stuurt via `src/proxy.ts` door op land (Cloudflare) en browsertaal. Pagina's worden bij het eerste verzoek gebouwd en 5 minuten gecachet (ISR), zodat het CDN ze kan bewaren en een build niet afhangt van de API.
- **Filters** staan in de URL en worden in de browser toegepast op de platen van de markt (65 items). Zo blijft er één gecachete pagina per markt.
- **Kleurstudio**: de SVG van de plaat staat inline; kleuren, tekst, leerblad en nummers zijn React-lagen erboven. Werk blijft alleen in de browser (localStorage), zonder account. Printen gebruikt het printvenster met een A4-printstijl.
- **Koelkast en boekje**: de koelkast bewaart opgehangen werk (kleuren en tekst) in `localStorage`, hooguit 24 platen, zonder account en zonder server. Het boekje (`/nl-nl/boekje?platen=kat,vis`) zet een voorblad met naam en de gekozen platen elk op een eigen A4, optioneel als kleur-op-nummer met kleurenlijst of als leerblad. De keuze staat in de URL, dus een boekje is te delen en er wordt niets bewaard. Printen gaat via het printvenster met een A4-printstijl; daar maakt de browser ook een PDF van.
- **SVG-assets** komen van `/v1/assets/...` met een eigen stijlblok en een vaste cache (`immutable`). In productie serveert Cloudflare ze; lokaal herschrijft Next ze naar de API.
- **Analytics**: `POST /e` op het eigen domein, zonder cookies. De route voegt het land toe, maakt een bezoekershash met een dagelijks wisselend zout en stuurt door naar de API. In productie kan dezelfde logica in een Cloudflare Worker draaien.
- **Fonts zelf gehost** (`@fontsource`), geen verzoeken naar Google.
- **CSP**: alleen eigen bronnen (`'self'`), geen externe scripts, geen frames. Scripts krijgen SRI-hashes. Inline scripts van Next blijven toegestaan omdat nonces dynamisch renderen vereisen, wat de CDN-cache uitschakelt. Afweging: cachebaarheid boven nonces; het risico is beperkt omdat er geen gebruikersinvoer in de HTML terechtkomt.
- **Admin panel (`apps/admin`)**: aparte Next.js-app, altijd dynamisch, `no-store` en `noindex`. Roept de admin-API server-side aan met het access token van de ingelogde beheerder (zie ADR 0007). Zonder Zitadel-configuratie werkt het alleen lokaal met `ADMIN_DEV_TOKEN`; in productie geeft het dan een 503.
