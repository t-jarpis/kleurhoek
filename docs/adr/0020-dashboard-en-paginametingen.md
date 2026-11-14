# 0020 · Dashboard met grafieken, paginametingen en accountcijfers

- Status: aangenomen
- Datum: 2026-10-24

## Aanleiding
Het dashboard toonde alleen totalen over 7 dagen. De eigenaar wil over een gekozen periode kunnen analyseren, zien hoeveel accounts er bijkomen en terugkomen, en weten welke pagina's bekeken worden. Dat moet binnen de privacyregels van ADR 0002 blijven.

## Besluit
- **Paginasoort, geen adressen.** Elke pagina stuurt `page_view` met haar soort (`home`, `plaat`, `boekje`, `account`), en de website voegt de organisatie toe (ADR 0017). Nooit de URL, zoektermen of verwijzer. De API weigert alles buiten dat patroon.
- **Dagtabellen die blijven.** `analytics.daily_pages` (dag, organisatie, soort pagina, markt, apparaat: weergaven en bezoekers) en `analytics.daily_visitors` (unieke bezoekers per dag per organisatie, en `*` voor de hele site). Ruwe events gaan na 90 dagen weg, zoals ADR 0002 al zei; dat gebeurt nu ook echt. Grafieken over 12 maanden lezen alleen dagtabellen.
- **Bezoekers zijn per dag uniek.** Het zout wisselt elke dag, dus over meer dagen is het een som van dagelijkse bezoekers. Het dashboard zegt dat erbij.
- **Terugkerende bezoekers tellen we niet.** Dat kan alleen door een browser te herkennen (cookie of opslag in de browser), en dat vraagt toestemming. **Terugkerende accounts** wel: accounts van vóór de periode die in de periode inlogden. Dat volgt uit de aanmaakdatum en de laatste inlog die we al bewaren; er komt geen gegeven bij. Het endpoint geeft alleen aantallen.
- **Overzicht-API** `GET /v1/admin/analytics/overview` en `GET /v1/admin/users/stats` (recht `analytics.read`): reeksen per dag (tot 92 dagen) of per week, totalen met de vorige periode van gelijke lengte, en verdelingen over pagina's, platen, apparaten, landen en organisaties.
- **Grafieken uit het design system** (Chart, BarList, StatCard met trend): eigen SVG zonder bibliotheek. Eén y-as, kleuren `chart-1..4` (gevalideerd op kleurenblindheid en contrast, licht en donker), legenda bij twee of meer reeksen, aanwijzen met muis, vinger of pijltjestoetsen, en elke grafiek ook als tabel.

## Afwegingen
- *Een grafiekbibliotheek* scheelt code, maar haalt een groot pakket in het admin panel en volgt het design system minder strak. Twee kleine componenten zijn genoeg.
- *Een "weekly active"-teller voor accounts per dag* vraagt een logboek van inlogdagen per persoon. Dat is meer persoonsgegevens dan nodig; de laatste inlog volstaat zolang de periode tot vandaag loopt.

## Aanvulling (2026-11-08): elke print telt
Tot nu toe telde een print alleen bij de printknop in de studio en het boekje. Prints via Ctrl+P, het browsermenu, de cadeaulabels en de extra pagina's misten. Nu telt ook het `beforeprint`-event van de browser (`components/PrintTracker.tsx` in de layout). Knop en event samen, binnen 5 seconden, tellen één keer. Staat er een plaat open in de studio, dan telt de print bij die plaat. Vanaf deze datum liggen de printaantallen daardoor hoger; vergelijk niet één op één met de periode ervoor.

## Aanvulling 14 november 2026: dubbel tellen en printen op iPhone
Op een iPhone telde één print twee keer, en kreeg je bij printen de melding "Voorkom verdere waarschuwingen voor deze pagina"; wie dan "Onderdruk waarschuwingen" koos, kon op die pagina niet meer printen tot herladen. Het printvenster verschijnt op iOS pas na een tel, dus een tweede tik vraagt een tweede venster. Daarom:
- Alle printknoppen gaan via `openPrint()` (`apps/web/src/lib/print.ts`): een tweede tik binnen 5 seconden, of binnen 1 seconde na het sluiten van het venster, doet niets.
- `trackPrint` telt binnen een minuut maar één keer (was 5 seconden), omdat Safari `beforeprint` ook later nog kan melden.
