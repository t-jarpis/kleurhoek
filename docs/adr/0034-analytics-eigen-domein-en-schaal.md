# 0034 · Analytics: eigen tab, eigen domein en hoe het meegroeit

- Status: aangenomen
- Datum: 2026-10-24

## Context
De eigenaar wil analytics zoals Matomo, maar zelf gebouwd en met privacy voorop. De cijfers stonden allemaal op het dashboard; dat werd te vol. De vraag was ook of Analytics een apart domein moet zijn en hoe het schaalt.

## Besluit
- **Analytics is al een eigen domein** (ADR 0001): eigen schema `analytics`, een vast contract om events aan te leveren (`POST /v1/internal/events` met `INGEST_KEY`, schema `EventInput`), en geen andere domeinen die zijn tabellen lezen. Dat blijft zo; het domein kan later als losse dienst draaien zonder dat de rest verandert.
- **Admin panel**: een eigen sectie **Analytics** met tabs Bezoekers, Bronnen (soort bron, domein, verwijzende sites), Inhoud (platen, prints, downloads, ingekleurd, winkelkliks), Apparaten en landen, Organisaties en **Nu op de site** (laatste 30 minuten). Het dashboard houdt alleen de kern: kerncijfers, grafieken en accounts, met een link naar Analytics.
- **Privacy zoals nu** (ADR 0002): geen cookies, geen IP-adres, een bezoekershash met een dagelijks zout; alleen soort pagina, hostnaam van de verwijzer, land, soort apparaat. Browser, scherm en besturingssysteem tellen we bewust niet (samen te herkenbaar). Ruwe events 90 dagen, dagtotalen blijvend.

## Hoe het meegroeit
1. **Nu (tot ongeveer een miljoen events per maand)**: Postgres, ruwe events plus dagtotalen die elke 10 minuten worden bijgewerkt. Het dashboard leest alleen dagtotalen; "Nu op de site" leest de ruwe events van 30 minuten (index op tijd).
2. **Groei (miljoenen events per maand)**: `analytics.events` per maand partitioneren (oude maanden weggooien = partitie droppen), het binnenhalen via een wachtrij laten lopen (Scaleway Queues of Cloudflare Queues) met een schrijver die in blokken invoegt, en dashboards laten lezen van een leesreplica. Geen wijziging aan de site of het contract.
3. **Veel groter**: Analytics als eigen dienst met een eigen database die voor tellen gemaakt is (bijvoorbeeld ClickHouse, of TimescaleDB als we Postgres willen houden). De website en de Worker sturen dan naar die dienst; het admin panel leest via dezelfde API-vorm. Dagtotalen blijven de bron voor lange periodes.
- Meetpunten om te beslissen: aantal events per dag, duur van het bijwerken van de dagtotalen (moet ruim onder 10 minuten blijven) en de grootte van `analytics.events`. Die komen in het operationele overzicht.

## Gevolgen
- Nieuw endpoint `GET /v1/admin/analytics/realtime`; het overzicht levert ook prints, downloads, "Wat heb je nodig"-weergaven en winkelkliks apart.
- Geen databasewijziging.
