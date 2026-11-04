# 0079 · Storingsmelding: elke 10 minuten controleren of de site werkt

- Status: aangenomen
- Datum: 2026-11-04

## Context
Na de DNS-wijziging van ADR 0071 was www.kleurhoek.be een tijd niet bereikbaar, en niemand kreeg daar een seintje van. Scaleway bewaart alleen logs (Cockpit). Health checks met meldingen in Cloudflare vragen een betaald plan.

## Besluit
- **GitHub Actions-workflow `Uptime`** (`.github/workflows/uptime.yml`) draait elke 10 minuten, en met de hand via "Run workflow".
- **Wat hij controleert:**
  - www.kleurhoek.nl;
  - www.kleurhoek.be/nl en /fr;
  - www.kleurhoek.com/en-gb;
  - het kale kleurhoek.nl (doorsturen);
  - een plaat-SVG via de website, wat ook de API test.
  
  Elk adres moet HTTP 200 geven met de verwachte inhoud. Elk adres krijgt twee pogingen met een pauze ertussen, zodat een enkele hapering niet als storing telt.
- **Melding:** bij een storing komt er één issue met het label `storing` waarin de eigenaar genoemd wordt, zodat GitHub hem mailt. Zolang dat issue openstaat, komt er geen nieuw. Werkt alles weer, dan sluit de workflow het issue zelf, met de duur van de storing.
- **Geen geheimen of nieuwe diensten:** de workflow gebruikt alleen het eigen token van de workflow (`issues: write`). Alles staat in de repo en gaat mee bij verkoop (ADR 0004).

## Gevolgen
- GitHub start geplande workflows soms een paar minuten later. Een storing zie je dus binnen ongeveer 10 tot 20 minuten.
- GitHub zet geplande workflows uit na 60 dagen zonder commits. Bij een stille periode moet je hem dan opnieuw aanzetten (Actions › Uptime › Enable).
