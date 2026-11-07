# 0087 · Oude adressen van een vorige eigenaar: 410

- Status: aangenomen
- Datum: 2026-11-07

## Context
kleurhoek.be had tot 2025 een andere eigenaar en een andere site. In Search Console stonden nog 101 sitemaps uit juli 2025 met honderdduizenden adressen. Google probeert die adressen nog steeds. Ze kwamen via twee doorverwijzingen (naar www, dan naar /nl) uit op een 404, en dat kost crawltijd die naar de nieuwe pagina's moet.

## Besluit
- Adressen die Kleurhoek zelf nooit gebruikt, geven direct een **410 Gone**, zonder doorverwijzing en met `X-Robots-Tag: noindex`. Het gaat om de oude sitemaps (`/sitemap-<nummer>.xml|txt`) en om pagina's op `.html`, `.php`, `.asp(x)`, `.jsp` of `.cgi` (`legacyGone` in `lib/guard.ts`). Dat geldt op elk domein.
- Een 410 laat Google sneller los dan een 404.
- De oude sitemaps zijn uit Search Console verwijderd.

## Gevolgen
- Eigen adressen zoals `/sitemap.xml`, `/sitemap/<markt>.xml`, `/robots.txt` en `/indexnow.txt` blijven werken; een test bewaakt dat.
- Duiken er in Search Console › Pagina's andere oude patronen op, dan komen die in dezelfde functie.
