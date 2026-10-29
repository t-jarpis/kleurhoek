# 0056 · Atelier: uitgebreide kleurstudio voor wie graag tekent

- Status: aangenomen
- Datum: 2026-10-29

## Context
De kleurstudio is gemaakt voor kinderen: je tikt op een vlak en het vlak krijgt een kleur. Thijs wil dat zo houden, en daarnaast meer mogelijkheden bieden aan mensen die graag tekenen en daar goed in zijn.

## Besluit
- **Schakelaar.** Een schakelaar "Atelier" in de kleurstudio. Het apparaat onthoudt de keuze (`kh:atelier`) en standaard staat hij uit. Uit is de studio precies zoals hij was.
- **Penselen die binnen de lijnen blijven.** Er zijn vijf penselen: potlood (met korrel), stift, waterverf (zachte, grillige rand), airbrush (nevel) en gum. Een streek blijft in het vlak waar hij begint.
  - Technisch komen de streken van een vlak in de SVG direct ná dat vlak, met het vlak zelf als clipPath. Wat erboven ligt, zoals ogen op een hoofd, blijft zo erboven.
  - Een kopie van het vlak tekent de lijn opnieuw over de streken.
  - De dikte volgt de druk van een pen (Apple Pencil, stylus) via `perfect-freehand`. Met muis of vinger wordt de druk nagebootst uit de snelheid.
- **Vullen.** Een vlak vullen kan effen, met een verloop (van de tweede kleur naar de eerste, mee met de zon als die aan staat) of met een patroon: stippen, strepen, ruitjes of golfjes. Met de pipet neem je de kleur van een vlak over. Een vulling blijft één tekst in de bestaande kleurenlijst (`g:…`, `p:…`), zodat koelkast, boekje en printen gewoon werken.
- **Kleuren.** Er zijn twee kleurvakjes, schuifjes voor tint, verzadiging en licht, en een hexveld. Verder rijen met passende kleuren (harmonie), lichter en donkerder, de laatst gebruikte kleuren en vijf sfeerpaletten.
- **De zon.** Je sleept een zonnetje rond. Elk gekleurd vlak krijgt dan een kopie met een verloop in zijn eigen omvang (objectBoundingBox): licht aan de kant van de zon, schaduw aan de andere kant. De kracht is instelbaar.
- **Lijnen.** De lijnkleur kan zwart, sepia, een eigen kleur of geen lijnen zijn.
- **Inzoomen.** Tot 600%, met knoppen, knijpen met twee vingers, Ctrl of ⌘ met het scrollwiel, of het trackpad. Schuiven gaat met twee vingers, de middelste muisknop of Alt.
- **Ongedaan maken en time-lapse.** Het werk is een lijst handelingen (vullen en streken). Ongedaan maken haalt de laatste weg. "Terugkijken" speelt de handelingen opnieuw af, waarbij lange streken groeien. Waar de browser het kan (MediaRecorder) wordt dat tegelijk opgenomen als filmpje (mp4 of webm). Ook opslaan als afbeelding (PNG, 2400 px) kan.
- **Alles op het apparaat.** Het werk staat in localStorage bij de plaat en op de koelkast. Er gaat niets naar de server en er is geen account nodig (ADR 0002).
- **Design system.** Nieuwe componenten ToolPicker, Range, ColorMixer, SunDial, ZoomBar en Dialog, plus iconen voor penselen en gereedschap.

## Gevolgen
- Werk met veel streken is groter in localStorage. Lukt opslaan niet meer, dan krijg je een melding en het advies om het werk als afbeelding op te slaan.
- Een afbeelding of filmpje wordt in de browser gemaakt. De opmaak gaat als regels in de SVG mee, maar eigen lettertypen (de naam onder de plaat) vallen terug op een standaardletter.
- Er komen geen nieuwe analytics-events bij. Het bestaande `plate_colored` telt ook het Atelier.
