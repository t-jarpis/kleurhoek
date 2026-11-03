# 0074 · Delen vanuit de kleurstudio

- Status: aangenomen
- Datum: 2026-11-03

## Context
Thijs wil dat mensen vanuit de plaat zelf kunnen delen: een lege plaat, hun eigen ingekleurde werk, of samen met iemand anders. Elke gedeelde link brengt bezoekers naar de site. Tegelijk kleuren (live) bestaat al (ADR 0060) en valt hierbuiten. Onder de plaat staat al "Bewaar op Pinterest" (ADR 0057).

## Besluit
- **Knop "Delen" in de studio** opent een dialoog (design system: ShareSheet) met vier opties:
  - *Mijn kleurplaat delen*: een PNG van het werk met het domein onderin, plus een link met de kleuren erin. Alleen als er iets is ingekleurd.
  - *Kleur jij de rest?*: de link met de kleuren. Wie hem opent, kleurt verder.
  - *Daag iemand uit*: de lege plaat met de vraag wie hem het mooist kleurt.
  - *Lege plaat delen*: alleen de link.
- **Kleuren in de link, niet op de server.** `?k=` bevat de vlakkleuren: de kleuren zonder #, gescheiden door punten, dan `~` en per vlak één teken. Er wordt niets bewaard. Hooguit 36 kleuren. Een verloop of patroon wordt de eerste kleur, net als bij de pipet. Een kapotte code wordt genegeerd.
- **Penseelstreken en eigen tekst gaan nooit mee**, niet in de link en niet in het plaatje. De eigen tekst is vaak een naam (ADR 0002). De dialoog zegt dat in één regel.
- **Delen gaat via het apparaat.** Eerst het deelmenu van het apparaat (`navigator.share`, met het plaatje als bestand als dat kan). Lukt dat niet, dan wordt het plaatje bewaard en verschijnen een gewone WhatsApp-link (`wa.me`) en "Kopieer link". Er zijn geen knoppen of scripts van sociale netwerken.
- **Plaatje vooraf maken.** Het plaatje wordt al gemaakt als het venster opengaat. Telefoons (vooral iOS) staan het deelmenu alleen direct na een tik toe, en tekenen duurt daarvoor te lang.
- **Filmpje delen.** In "Zo heb je het gemaakt" (Atelier) staat naast Opslaan de knop *Deel filmpje*: de time-lapse als mp4 of webm via het deelmenu, met een link naar de lege plaat. Alleen als het apparaat bestanden kan delen. Staat er eigen tekst op de plaat, dan vraagt het venster die eerst weg te halen, omdat het filmpje die tekst laat zien.
- **Meten zonder cookies.** Een event `share` als iemand deelt of de link kopieert. Een event `shared_visit` als iemand binnenkomt via een link met `?d=1`. De parameters gaan daarna uit de adresbalk. In de dagtotalen komen `shares` en `shared_visits`, ook per plaat. Het dashboard toont "Gedeeld" met het aantal bezoeken via een gedeelde link.

## Gevolgen
- Een gedeelde link toont de gewone plaat als voorbeeld (Open Graph). Een ingekleurd voorbeeld per link zou de plaatpagina dynamisch maken. Dat doen we pas als blijkt dat het nodig is.
- Wie een link met kleuren opent, begint met die kleuren in plaats van met zijn eigen bewaarde werk op die plaat. De studio meldt dat.
- Migratie `0030_analytics_shares` voegt de twee kolommen toe aan de dagtotalen.
