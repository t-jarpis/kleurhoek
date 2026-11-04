# 0078 · Ruwe events bewaren, bezoekerscode na 90 dagen onherleidbaar

- Status: aangenomen (vervangt de bewaartermijn van 90 dagen voor ruwe events uit ADR 0002)
- Datum: 2026-11-04

## Context
Volgens ADR 0002 gingen ruwe events na 90 dagen weg en bleven alleen de dagtotalen. Daardoor kon een nieuw cijfer maar 90 dagen terug worden berekend. Dat was te zien bij online gekleurd (ADR 0077) en bij de tijdstippen van downloads (ADR 0073). Thijs wil de hele geschiedenis kunnen bekijken en vergelijken, maar hoeft niet te weten wie iets deed.

Het enige gegeven in een event dat naar een apparaat wijst, is de bezoekerscode: een hash van IP-adres en user agent, met een zout dat dagelijks wisselt maar uit een vast geheim komt. Met dat geheim en iemands IP-adres en browser zou je kunnen nagaan of die persoon op een dag langskwam. De rest is niet persoonlijk: soort, plaat, markt, land, apparaatsoort, tijdstip, organisatie en de hostnaam van de verwijzer.

## Besluit
- **Ruwe events blijven bewaard**, zonder einddatum.
- **Na 90 dagen nieuwe codes** (`anonymizeRawEvents`, in de uurlijkse telling). Per hele dag (UTC) krijgt elke bezoekerscode een nieuwe code: `'~' || sha256(sleutel || code)`. De sleutel is willekeurig, per dag anders, en wordt nergens bewaard.
  - Binnen een dag blijft hetzelfde apparaat herkenbaar. Unieke bezoekers, "per bezoek" en nieuwe cijfers kloppen dus ook als je oude dagen opnieuw telt.
  - Over dagen heen kun je niets koppelen.
  - Terug naar IP-adres en browser kan niemand meer, ook wij niet.
- **Het tijdstipoverzicht** (ADR 0073) beslaat nu de hele gekozen periode in plaats van hooguit 90 dagen.
- **De privacytekst** zegt hoe bezoekers geteld worden en dat de code na 90 dagen wordt vervangen.

## Gevolgen
- De events-tabel groeit door. Bij veel verkeer komen er eerst maandpartities (zoals in ADR 0034), daarna eventueel een eigen opslag om te tellen.
- `staleDays` en `aggregateDay` werken op elke dag, zodat nieuwe kolommen de hele geschiedenis kunnen aanvullen.
- Na 90 dagen is een bezoek binnen één dag nog als reeks te zien, maar niet aan iets buiten de database te koppelen. Dit is geen juridisch advies; bij twijfel laten toetsen.
