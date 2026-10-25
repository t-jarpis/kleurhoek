# 0040 · Een domein per land, en Belgische markten

- Status: aangenomen
- Datum: 2026-10-25
- Vervangt deels: ADR 0013 (doorsturen van .be en .com), ADR 0032 (`?via=` als enige bron voor het domein)

## Context
Kleurhoek draaide alleen op www.kleurhoek.nl met de markt in het pad (`/nl-nl/…`). kleurhoek.be en kleurhoek.com stuurden door naar de Nederlandse site. Er komen Belgische bezoekers in het Nederlands en het Frans. België heeft andere feestdagen en datums dan Nederland, en een Franstalige bezoeker hoort niet automatisch op een Nederlandse site te belanden. Voor zoekmachines is een domein per land (ccTLD) het sterkste signaal voor het land.

## Besluit
- **Per land een domein, elke markt op een vast adres:**
  - kleurhoek.nl: nl-NL op de wortel (`/platen/kat`).
  - kleurhoek.be: nl-BE op `/nl`, fr-BE op `/fr`.
  - kleurhoek.com: elke andere markt op `/<markt>` (`/de-de/…`). Op .com staan alle feestdagen, omdat we daar geen kalender per land hebben.
- **Niet doorsturen op browsertaal**, zoals Google aanraadt. Er is één uitzondering: de beginpagina van kleurhoek.be kiest Nederlands of Frans op de browsertaal (302, `Vary: Accept-Language`, standaard Nederlands). Op kleurhoek.com kiest de beginpagina de beste markt op land en taal.
  - Spreekt de browser een andere taal die we ook hebben, dan verschijnt een rustige banner in die taal met een link. Wegklikken wordt op het apparaat onthouden.
  - Onderaan elke pagina staat een taalkeuze. Die gaat naar dezelfde pagina in de andere markt.
  - Design system: MarketSwitch.
- **Oude adressen** (`/nl-nl/…`, `/nl-be/…`) gaan met 301 naar het nieuwe adres, ook als dat op een ander domein ligt. Dat geldt ook voor de links in eerder verstuurde mails.
- **Routering in de website-proxy** (`lib/sites.ts`), alleen voor Kleurhoek zelf en alleen als `SITE_DOMAINS` gezet is. Organisatiesites, lokaal en docker compose houden `/<markt>`.
  - Links in de site lopen via een voorvoegsel per markt (`baseFor`, `useHref`).
  - Absolute adressen (canonical, hreflang, sitemap, gestructureerde gegevens) lopen via `pageUrl`.
- **Zoekmachines:**
  - hreflang en canonical gaan over de domeinen heen. x-default op de beginpagina wijst naar kleurhoek.com.
  - Per domein is er een eigen robots.txt en sitemap, met alleen de eigen adressen en de taalversies op de andere domeinen.
  - Alle drie de www-hosts zijn indexeerbaar.
- **Infrastructuur:** de .be- en .com-zones krijgen `www` (prod) en `dev` (dev) via de bestaande Worker. Module `market-domain` vervangt `redirect-domain`.
  - De Worker kent die hosts via de binding `HOSTS`, stuurt ze naar de website van de omgeving en geeft de echte host mee.
  - De website markeert eigen redirects naar een ander domein met `x-kh-keep-location`, zodat de Worker het adres laat staan.
  - Het kale domein stuurt door naar www.
  - Inloggen werkt per domein: een eigen terugkeeradres en een eigen sessiecookie. Die adressen staan in Zitadel.
- **Markten:** nl-BE en fr-BE staan live (seed). De website leest de live markten uit `MARKETS` tijdens het draaien, niet bij het bouwen, zodat één image op dev en prod past.
- **Feestdagen per land:** een feestdag heeft landen en per land afwijkingen (`overrides`).
  - Sinterklaas valt in België op 6 december.
  - Vaderdag valt in België op de tweede zondag van juni.
  - De eerste schooldag is in België op 1 september.
  - Koningsdag, Bevrijdingsdag en Keti Koti zijn alleen Nederlands.
  - De Belgische nationale feestdag (21 juli) is nieuw.
  - Platen van een feestdag die in dat land niet gevierd wordt, zijn er niet te zien.
  - Een land zonder kalender krijgt alle feestdagen.
  - Feestdagen en seizoenen worden bij elke start bijgewerkt uit catalog-data, want ze zijn niet te bewerken in het admin panel.
- **Frans:** alle platen die niet taalgebonden zijn, plus de woordenlijst van de teksten in platen, zijn vertaald. `check-lang.mjs fr` geeft geen problemen.

## Gevolgen
- Migratie 0025: `availability.holidays.overrides`.
- `/mail/bevestig` (POST) is de nieuwe naam van de route om een aanmelding te bevestigen. Op kleurhoek.nl zijn `/mail` en `/mail/bevestigen` pagina's.
- De binnenkomsttelling (ADR 0032) leest het domein uit de host. `?via=` blijft werken voor oude links.
- De rooktest na een deploy volgt redirects (`/nl-nl` → `/`).
- Uitrollen: `scripts/infra.sh up` (zone, dev, prod) zet DNS, Worker-routes, `SITE_DOMAINS` en de Zitadel-adressen. Tot die tijd blijft het oude schema actief, met de Belgische markten op `/nl-be` en `/fr-be`.
