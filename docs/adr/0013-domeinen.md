# 0013 · Domeinen: kleurhoek.nl als hoofddomein, .be en .com sturen door

- Status: aangenomen
- Datum: 2026-10-22

## Context
De eigenaar heeft `kleurhoek.nl`, `kleurhoek.be` en `kleurhoek.com` geregistreerd bij Neostrada (22-10-2026). De site werkt met markten in het pad (`/nl-nl`, later `/nl-be`, `/de-de`; ADR 0003), op één domein. Eén domein houdt cookies, inloggen (Zitadel-redirects), Cloudflare Access en SEO eenvoudig.

## Besluit
- **`kleurhoek.nl` is het hoofddomein**: `www.kleurhoek.nl` (site), `admin.kleurhoek.nl` (beheer), `dev.` en `admin-dev.` voor dev, later `login.kleurhoek.nl` voor Zitadel. Het kale domein stuurt door naar www.
- *(Vervangen door ADR 0040: elk land een eigen domein.)* **`kleurhoek.be` en `kleurhoek.com` sturen door** naar `https://www.kleurhoek.nl`, met pad en query (301), via Cloudflare (module `infra/modules/redirect-domain`, alleen prod). Ze bestaan om de naam te beschermen en voor wie het adres intypt.
- Alle drie de domeinen staan als zone in hetzelfde Cloudflare-account van Kleurhoek (gratis plan voor `.be` en `.com`), zodat ze bij verkoop meegaan (ADR 0004). De registratie staat bij Neostrada; bij verkoop worden de domeinen verhuisd.

## Later
- Als de Belgische markt live gaat, kan `kleurhoek.be` doorsturen naar `/nl-be` (en `/fr-be` op taal), of een eigen hostnaam krijgen. Dat is een aparte beslissing: een eigen domein per markt vraagt extra redirect-URI's in Zitadel en een eigen Access-configuratie.
- `kleurhoek.com` kan de internationale ingang worden (taalkeuze), zodra er een tweede taal is.
