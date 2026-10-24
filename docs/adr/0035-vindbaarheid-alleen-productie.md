# 0035 · Vindbaarheid: alleen www.kleurhoek.nl in zoekmachines

- Status: aangenomen
- Datum: 2026-10-24

## Context
De site draait op meerdere plekken: productie (www.kleurhoek.nl), dev, lokaal en de sites van organisaties (subdomein of eigen domein, ADR 0017). Tot nu toe kregen alleen organisaties `noindex`. Dev kon dus in zoekmachines komen als dubbele inhoud, er was geen sitemap, geen canonieke URL en geen taalversies, en de omschrijving van een plaat stond vast in het Nederlands.

## Besluit
- **Alleen Kleurhoek zelf op het productieadres** wordt geïndexeerd: `SITE_URL` is `https://www.kleurhoek.nl` én de organisatie is de standaardorganisatie (`lib/seo.ts`, `indexable`). Al het andere krijgt `robots: noindex, nofollow` en een robots.txt met `Disallow: /`. Organisaties worden dus nooit geïndexeerd; hun site is van hen, niet een tweede ingang voor Kleurhoek.
- **robots.txt en sitemap.xml** zijn routes van de website, buiten het organisatiepad (`SHARED_PATH`). Ze kijken naar de host: alleen www.kleurhoek.nl in productie krijgt een open robots.txt en een sitemap; elders is de sitemap 404.
- **Sitemap**: per live markt de voorpagina, thema's, contact, disclaimer en eigen omgeving, elke plaat en elk thema, met `hreflang`-taalversies en `x-default`. Platen staan alleen in de markten waar ze zichtbaar zijn (ADR 0029), dus de taalversies volgen vanzelf.
- **Per pagina**: canonieke URL, taalversies voor pagina's die in elke markt bestaan, omschrijving van een plaat in de taal van de markt (`metaPlate`), Open Graph, en gestructureerde gegevens (`CreativeWork` per plaat, `WebSite` op de voorpagina). Account en boekje blijven `noindex`; `/auth`, `/ga` en `/e` staan in robots.txt als `Disallow`.
- **Instellingen in het admin panel** (Inhoud › Vindbaarheid, rechten `seo.read` en `seo.manage`): verificatiecode voor Google Search Console en Bing (meta-tag, alleen op productie) en per markt de titel en omschrijving van de voorpagina, met een voorbeeld in zoekresultaten (design system: SnippetPreview). Ze staan op de standaardorganisatie (`organizations.seo`, migratie 0020); de API geeft ze alleen voor die organisatie aan de website.

## Gevolgen
- Een nieuwe omgeving (staging, preview) is vanzelf afgeschermd; er is niets om te vergeten.
- Wordt het productieadres ooit anders, dan verandert `PRODUCTION_SITE` in `lib/seo.ts` en `indexableHost` in de API mee.
- Na livegang: de site aanmelden in Search Console en Bing met de codes uit het admin panel en daar de sitemap opgeven.
- Thema-pagina's hebben nog een vaste Nederlandse titel; die gaan mee als de bronnengids meertalig wordt.
