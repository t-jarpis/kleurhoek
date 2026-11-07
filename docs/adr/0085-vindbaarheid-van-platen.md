# 0085 · Vindbaarheid van platen: titels, andere namen en afbeeldingen in de sitemap

- Status: aangenomen
- Datum: 2026-11-07

## Context
Search Console werkt sinds 7 november (ADR 0041). De eerste twee weken lieten drie dingen zien:
- **Weinig klikken.** Platen staan voor zoekwoorden als "smoothie kleurplaat" en "bouwplaat auto" al op plek 1 tot 10, maar er wordt nauwelijks op geklikt.
- **Eentonige, soms dubbele titels.** Elke beschrijving was dezelfde zin, bij kaarten en tekenlessen met een dubbel woord ("Kaart Kaart: welkom thuis!").
- **Zoekwoorden die we niet gebruiken.** Mensen zoeken met woorden die niet in onze namen staan. "Langnek dino" gaf 30 vertoningen, maar we stonden op plek 44, omdat onze plaat "Dino met lange nek" heet.

Daarnaast noemde de sitemap de afbeeldingen van de platen niet, terwijl veel ouders via Google Afbeeldingen zoeken.

## Besluit
- **Titel per plaat** volgt hoe mensen zoeken: in het Nederlands "Fruitsmoothie kleurplaat – gratis printen", in de andere talen "Naam – soort, gratis printen" in die taal (`plateTitle`).
  - De soort staat er niet dubbel in: staat hij al in de naam, dan valt hij weg (`kindFor`).
  - Alt-teksten en Pinterest houden de korte vorm (`metaPlateTitle`), ook zonder dubbele soort.
- **Beschrijving** is de bestaande zin, aangevuld met onderwerp, leeftijd en andere namen ("Dino's · 4–6 jaar. Ook bekend als: langnek, brachiosaurus."), zodat elke plaat een eigen tekst heeft.
- **Andere namen** (synoniemen) per plaat en taal staan in `catalog-data/synonyms.json`, apart van `plates.json` zodat ze makkelijk na te kijken zijn.
  - Ze komen in de vertaling als veld `also`. Catalog-data is daarvoor de bron: bij elke start werkt de API ze bij, ook voor bestaande platen, in één statement en alleen waar ze verschillen.
  - De API geeft ze mee als `also`.
  - De website toont ze op de plaatpagina ("Ook bekend als: …"), zet ze in de beschrijving en als `alternateName` in de gestructureerde data, en de zoekbalk (ADR 0084) zoekt erin.
  - Geen merken of bekende figuren.
  - De lijst Gezocht (ADR 0084) laat zien welke andere namen nog ontbreken.
- **Sitemap met afbeeldingen:** bij elke plaat een `image:image` met de PNG (Google-extensie voor afbeeldingen).

## Gevolgen
- Er is geen migratie nodig: `also` is een extra veld in de bestaande vertalingen.
- Andere namen staan er voor alle 29 talen: in het Nederlands voor 590 platen, in de andere talen voor 336 tot 636 platen per taal. Per taal is gekeken wat mensen daar echt typen, dus geen letterlijke vertaling; regionale woorden staan erbij (Belgisch, Oostenrijks/Zwitsers, Braziliaans/Portugees, Latijns-Amerikaans). Buitenlandse feestdagen die iets anders betekenen, staan er niet bij, zoals 25 april bij de plaat over 5 mei.
- De titels van alle platen veranderen tegelijk. Search Console laat over een paar weken zien of het aantal klikken stijgt.
- De web-tests kennen nu het `@/`-pad (vitest.config.ts), zodat ook modules als de sitemap te testen zijn.
