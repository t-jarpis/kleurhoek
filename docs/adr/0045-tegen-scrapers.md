# 0045 · Scrapers tegengaan, met de herkomst op elke plaat

- Status: aangenomen
- Datum: 2026-10-25

## Context
De platen staan publiek online; dat is de bedoeling. Wat we niet willen: sites die onze platen massaal overnemen of rechtstreeks vanaf onze server tonen, en AI-bedrijven die ze gebruiken om modellen te trainen. Helemaal tegenhouden kan niet: een vastberaden scraper doet zich voor als een gewone browser. Het kan wel lastiger en minder lonend. Zoekmachines (Google, Bing) moeten er gewoon bij blijven.

## Besluit
- **robots.txt:** crawlers die AI-modellen trainen mogen niets. Het gaat onder meer om GPTBot, CCBot, Google-Extended, Applebot-Extended, Bytespider, ClaudeBot, PerplexityBot en Amazonbot. Zoekmachines blijven welkom.
- **Cloudflare "Block AI bots"** op alle drie de domeinen (gratis). Dat houdt ook AI-crawlers tegen die robots.txt negeren.
  - Bewust géén Bot Fight Mode: die is op het gratis plan niet uit te zonderen, en zou de webhooks van de mailrelay, onze rooktests en de Worker blokkeren.
- **Hotlinking:** een plaatbestand (SVG) dat een andere site als afbeelding in haar pagina zet, krijgt een 403.
  - Dit gebeurt in een Cloudflare-firewallregel vóór de cache, met daarnaast een controle in de website-proxy.
  - Eigen domeinen, organisatiesites, zoekmachines en het rechtstreeks openen van een bestand blijven werken.
  - PNG's (voor mails) vallen er niet onder.
- **Paginalimiet:** hooguit 300 pagina's per minuut per IP-adres, in het geheugen van de website. Prefetch en interne verzoeken tellen niet mee, en bekende zoekmachines en onze rooktests evenmin. Een hele klas achter één adres haalt dit niet, een scraper wel.
- **Herkomst op de plaat (PlateMark):**
  - Onder elk vel staat klein het domein van de markt (kleurhoek.nl, .be of .com), op het scherm en op papier. Dit geldt voor de kleurstudio en het boekje.
  - Op een eigen omgeving van een organisatie staat het er niet. Dat is een van de voordelen van een eigen omgeving, en staat ook zo op de pagina Eigen omgeving.

## Gevolgen
- De Cloudflare-instellingen werken na `scripts/infra.sh up`. Weigert Cloudflare de bot-instelling op rechten, voeg dan "Bot Management: Edit" aan het token toe of zet `block_ai_bots = false`.
- De losse SVG-bestanden zelf blijven zonder vermelding. De vermelding zit in het vel dat mensen zien en printen.
