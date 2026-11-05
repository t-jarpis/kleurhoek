# 0083 · Bij elke download: hoe dat bezoek binnenkwam

- Status: aangenomen
- Datum: 2026-11-05

## Context
Thijs zag één download van één heel specifieke plaat en wilde weten hoe iemand daar terechtkwam. De lijst Laatste downloads en prints (ADR 0073) toonde alleen tijd, plaat, markt en apparaat. De binnenkomst (verwijzende site en eerste pagina, ADR 0032) en de bezoekerscode van één dag bestonden al, maar werden niet aan elkaar gekoppeld.

## Besluit
- De API zoekt bij elke download en print in de lijst de laatste binnenkomst van hetzelfde bezoek. Dat gebeurt via de bezoekerscode, alleen op dezelfde (UTC-)dag en alleen vóór de download. De API geeft daarvan alleen de hostnaam van de verwijzer, het domein van binnenkomst en de soort pagina terug.
- De bezoekerscode zelf verlaat de API niet.
- Het admin panel toont dat als kolom **Kwam binnen via**, bijvoorbeeld "google.com → een plaat" of "rechtstreeks → de voorpagina". Zonder binnenkomst staat er "—". Design system: ActivityHeatmap.
- Er wordt niets extra's bewaard. Er gaat ook niets over meerdere dagen heen: de code wisselt elke dag.

## Gevolgen
- Met weinig bezoekers is één regel heel specifiek. De kolom staat daarom alleen in het admin panel en gaat nooit in een export of rapport.
- Zoektermen staan hier niet in. Die komen uit Search Console (ADR 0041), per pagina en niet per bezoek.
