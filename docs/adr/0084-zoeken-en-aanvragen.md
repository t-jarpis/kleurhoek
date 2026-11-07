# 0084 · Zoeken op de site, en bijhouden wat we nog niet hebben

- Status: aangenomen
- Datum: 2026-11-07

## Context
Bezoekers konden alleen bladeren met filters (onderwerp, leeftijd, soort). Met meer dan 1100 platen is dat traag, en we wisten niet welke platen mensen zochten die we niet hebben. Thijs wilde een zoekbalk, het automatisch bijhouden van wat er niet gevonden wordt, en dat bezoekers een plaat kunnen aanvragen, zodat ze zich geholpen voelen.

## Besluit
- **Zoekbalk** boven de filters van het platenraster (design system: PlateSearch). Het zoeken gebeurt in de browser, over de platen die de pagina al heeft: naam, onderwerp, feestdag, werelddeel, land, soort en leerdoel. Hoofdletters, accenten en leestekens tellen niet mee; een meervoud vindt ook het enkelvoud. Werkt samen met de filters, en de tellers van de filters lopen mee. Het zoekwoord staat in `?q=`. Er komt geen zoekserver bij.
- Past het zoekwoord bij een thema uit de Bronnengids (ADR 0025), dan staat er een link naar de officiële platen bij de makers. Zelf maken we geen merken of bekende figuren.
- **Niets gevonden in alle platen:** "Die hebben we nog niet" met de knop **Vraag deze plaat aan**. Daarna volgt een bedankje, met op Kleurhoek zelf een link naar de mail over nieuwe platen.
- **Bijhouden:** de website stuurt het zoekwoord naar `/w`. Dat gebeurt als niets gevonden is (`miss`, na 1,5 seconde stilstand) of als iemand op aanvragen klikt (`request`). `/w` geeft het door aan de API (`/v1/internal/wishes`, zelfde sleutel en nieuwe pogingen als de events, ADR 0082).
  - Er wordt alleen het zoekwoord bewaard, gelijkgemaakt en hooguit 40 tekens, met de markt, de dag en de bezoekerscode van die dag. Die code dient tegen dubbel tellen en gaat na 90 dagen weg (ADR 0078).
  - Woorden met @, een webadres of een reeks van 4 of meer cijfers worden niet bewaard. Zo komen er geen e-mailadressen of telefoonnummers in.
  - Elk woord telt één keer per bezoeker per dag. De browser stuurt een woord ook maar één keer per bezoek, en onthoudt een aanvraag tot morgen (`kh:gevraagd`, alleen op dit apparaat).
- **Admin panel, Analytics › Gezocht:** per zoekwoord het aantal bezoekers dat het miste, het aantal aanvragen, de markten en de laatste dag.
  - Gemiste woorden en aanvragen staan er meteen, vanaf 1 bezoeker (`MISS_THRESHOLD`). Met nog weinig bezoekers wil Thijs elk signaal zien. Als de lijst vol raakt met tikfouten of namen, gaat de drempel omhoog (bijvoorbeeld naar 3). Woorden onder de drempel worden wel bewaard en verschijnen dan alsnog.
  - Status Open, Gemaakt of Verborgen, met de nieuwe permissie `analytics.wishes.manage` (in de rol Contentbeheerder). Elke wijziging komt in het auditlog en is ongedaan te maken (`UndoRegistry`).
- Cloudflare: `/w` valt onder dezelfde rate limit als `/e`.

## Gevolgen
- Nieuwe tabellen `analytics.search_wishes` en `analytics.search_wish_status` (migratie 0032), met row-level security.
- Zoekwoorden zijn vrije tekst van bezoekers, soms kinderen. Daarom gelden de filters tegen persoonsgegevens en de status Verborgen (een naam of iets persoonlijks: verbergen). De lijst staat alleen in het admin panel en gaat nooit in een export.
- Zoeken werkt alleen op de voorpagina, waar het raster staat. Een zoekserver of zoeken in de plaatbeschrijvingen kan later, als de catalogus veel groter wordt.
- Zoeken zelf telt niet als event: zoekwoorden met resultaat worden niet bewaard.
