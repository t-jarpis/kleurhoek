# 0032 · Binnenkomst per domein en verwijzende site

- Status: aangenomen
- Datum: 2026-10-24

## Context
Kleurhoek is bereikbaar via kleurhoek.nl, kleurhoek.be en kleurhoek.com. De laatste twee sturen door naar www.kleurhoek.nl (ADR 0021), dus de site ziet niet via welk domein iemand kwam. De eigenaar wil weten waar het verkeer vandaan komt: welk domein, en van welke site (zoekmachine, Pinterest, direct).

## Besluit
- **Doorverwijzing met code**: kleurhoek.be en kleurhoek.com sturen door met `?via=be` of `?via=com` (Terraform, module `redirect-domain`; een bestaande query blijft staan, `&via=` komt erachter). Geen code = kleurhoek.nl.
- **Alleen de binnenkomst telt**: bij de eerste paginaweergave van een bezoek van buitenaf stuurt de site het domein (`nl`, `be`, `com`) en de **hostnaam** van de verwijzende site mee (`google.com`, `pinterest.com`; leeg = direct of onbekend). Nooit een pad, zoekterm of volledige URL. Navigeren binnen de site telt niet opnieuw.
- Daarna haalt de site `via` uit de adresbalk, zodat het niet in gedeelde links terechtkomt.
- Opslag: twee kolommen in `analytics.events` (`entry_domain`, `referrer`), en dagtotalen in `analytics.daily_sources` (dag, organisatie, domein, verwijzer, binnenkomsten, bezoekers). De dagtotalen blijven na de 90 dagen van de ruwe events.
- **Dashboard**: "Binnengekomen via domein" en "Verwijzende sites" (top 15, de rest als "Overige sites").
- Privacy (ADR 0002): geen cookies, geen IP-adres; een hostnaam van een verwijzer zegt niets over een persoon.

## Gevolgen
- De telling per domein begint pas als de eigenaar Terraform voor de zone uitvoert (de redirect-regels veranderen). De verwijzende sites worden meteen na de uitrol geteld.
- Cloudflare toont per zone ook zelf het aantal verzoeken; dat is een grove controle (inclusief bots), deze telling is het eigen, schone getal.
