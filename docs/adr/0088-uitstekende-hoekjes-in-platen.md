# 0088 · Uitstekende hoekjes in platen opsporen

- Status: aangenomen
- Datum: 2026-11-07

## Context
In een plaat wordt een been of arm vaak "onder" een later vlak gestopt: het been begint binnen de buik, en de buik wordt eroverheen getekend. Begint het been net naast de buik, dan steekt er een hoekje uit. Thijs zag dat bij het voorbeen van het paard in "Sinterklaas op zijn paard", op een pin. Zulke foutjes vallen bij het maken niet op en blijven anders staan.

## Besluit
- `scripts/plates/stubs.mjs` loopt in een echte browser langs de omtrek van elk vlak, kijkt welk stuk bedekt is door een vlak dat later getekend wordt, en zoekt een kort recht stuk (de "dop" van een been of arm) dat deels zichtbaar is tussen twee veel langere stukken, met minstens 5 eenheden zichtbaar (minder valt weg in de lijn).
- `scripts/plates/check.mjs` meldt dat als **waarschuwing**, niet als fout: de controle vindt ook bedoelde T-verbindingen, tegels en patronen. Een mens kijkt en beslist.
- `scripts/plates/relabel.mjs <slug>` berekent na een kleine reparatie aan een bestaande tekening de posities van de nummers opnieuw; teksten, kleuren en volgorde blijven staan.
- Eerste ronde over alle 554 kleurplaten: hersteld zijn sinterklaas (voorbeen), theepot (oor), herfstwandeling (stam) en hobbelpaard (oor). De rest bleek bedoeld of te klein om te zien.

## Gevolgen
- Een herstelde tekening wordt bij de volgende uitrol vanzelf een nieuwe versie (ADR 0064): nieuw adres voor SVG en PNG, opgeslagen kleurwerk blijft bij de oude versie.
- Pins en posts die al gedeeld zijn, houden het oude plaatje.
- De controle kan scherper als de lijst met waarschuwingen te lang wordt, bijvoorbeeld door alleen te melden waar het bedekkende vlak zijn rand deelt met de dop.
