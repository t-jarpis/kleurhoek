# 0047 · Vindbaarheid per markt: standaardteksten, titels en schrijfwijze

- Status: aangenomen
- Datum: 2026-10-26

## Context
Met veertien markten (ADR 0046) stond de vindbaarheid nog op Nederland ingesteld. De voorpagina had zonder invulling in het admin panel alleen "Kleurhoek" als titel. Plaatpagina's hadden alleen de naam van de plaat als titel, zonder het woord waarop mensen zoeken ("kleurplaat", "Ausmalbild", "coloring page"). Themapagina's hadden een vaste Nederlandse titel. `<html lang>` gaf alleen de taal ("en") en niet het land. Voor en-US stonden er Britse spelling en A4 in de omschrijvingen, en voor de-CH de ß.

## Besluit
- **Standaardteksten voor de voorpagina** staan per markt in `catalog-data/seo.json`: titel tot 60 tekens en omschrijving tot ongeveer 150 tekens, met de zoekwoorden van dat land. Voorbeelden: "kleurprenten afdrukken" (BE), "Ausmalbilder kostenlos ausdrucken" (DE), "Malvorlagen" (AT), "free printable coloring pages" (US), "dibujos para colorear" (ES), "disegni da colorare" (IT) en "kolorowanki do druku" (PL).
- **De API vult ze bij het starten in** op de standaardorganisatie (`OrganizationsService.fillSeoDefaults`), alleen voor markten waar titel en omschrijving allebei leeg zijn. Wat in het admin panel (Inhoud › Vindbaarheid) staat, blijft staan; de teksten zijn daar te zien en aan te passen. Maak je beide velden leeg, dan komt de standaardtekst bij de volgende start terug.
- **Titels per pagina in de taal van de markt:**
  - Een plaat krijgt "naam – soort", bijvoorbeeld "Katze auf einem Kissen – Malvorlage".
  - Een thema krijgt een eigen titel en omschrijving per taal (`metaThemeTitle`, `metaTheme`).
- **Schrijfwijze per markt:** `messages()` neemt ook een marktcode aan.
  - en-US krijgt Amerikaanse spelling (color, favorite, organization) en Letter in plaats van A4.
  - de-CH krijgt "ss" in plaats van "ß".
  - Andere markten vallen terug op hun taal. Pagina's geven de markt door, dus titels, omschrijvingen en paginateksten volgen de variant. Componenten die alleen de taal krijgen, blijven Brits Engels of gewoon Duits.
- **`<html lang>`** krijgt taal én land (`en-US`, `de-CH`), net als hreflang.

## Gevolgen
- Een nieuwe markt krijgt standaardteksten door één regel toe te voegen aan seo.json.
- De vertalingen van platen blijven per taal. Plaatnamen voor en-US houden dus Britse spelling waar die erin staat (zelden).
- Verificatie bij Google loopt via de domeineigenschap (DNS). Bing en het opgeven van de sitemaps per domein doet Thijs in Search Console en Bing Webmaster Tools.
