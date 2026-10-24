# 0022 Doelen in het admin panel

Datum: 24-10-2026. Status: aangenomen.

## Context
We willen zien of Kleurhoek groeit zoals verwacht. Vergelijkbare Nederlandse kleurplatensites halen via Google tientallen tot honderdduizenden bezoeken per maand, met honderden tot duizenden platen. Een nieuwe site begint met een paar honderd bezoeken.

## Besluit
- Drie doelen per maand: **bezoeken** (som van unieke bezoekers per dag, hele site), **platen online** (gepubliceerde platen aan het eind van de maand) en **doorkliks naar winkels**.
- Per doel tussendoelen (maanden na de start, doel en ambitie). Daartussen loopt de lijn recht, na het laatste blijft hij gelijk. Startwaarden: bezoeken 500 → 3.000 (maand 6) → 10.000 (maand 12), ambitie 30.000; platen 66 → 300, ambitie 500; doorkliks 10 → 100 (ongeveer 10 verkopen, de drempel voor productfoto's van Amazon), ambitie 300.
- Opslag in `analytics.goals` (één rij per meetwaarde, tussendoelen als JSON). Zonder opgeslagen doelen begint de reeks in de eerste maand met bezoekers.
- Pagina **Doelen** in het admin panel: per doel een GoalCard (deze maand naar rato van de dagen, op koers of achter) en een grafiek met werkelijk, doel (gestreept) en ambitie (gestippeld). Bekijken met `analytics.read`, wijzigen met het nieuwe recht `analytics.goals.manage` (alleen platformbeheerders), met auditregel.
- Het domein Analytics leest het aantal platen via de publieke `CatalogService` (geen tabellen van Catalogus).

## Gevolgen
- Doelen zijn per omgeving: dev en prod hebben elk hun eigen doelen.
- Seizoenen (december, Sint-Maarten) zitten niet in de lijn; die pieken staan boven het doel.
