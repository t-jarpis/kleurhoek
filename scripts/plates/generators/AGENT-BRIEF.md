# Opdracht: één batch printbare werkjes voor Kleurhoek (kinderkleurplaten-site)

Repo: /home/claude/kleurhoek. Generators in scripts/plates/generators (Python). Lees eerst:
- kit.py (Sheet: region/circle_r/ellipse_r/poly_r/rect_r = kleurvlak met kleurcode; line/seg/rect_line/circle_line = lijn; cls "cut" knippen, "fold" vouwen, "glue" (raw rect), "guide" hulplijn; text, dot, legend, write)
- lib_gen.py (card, outline_text, star_pts, cap, lesson, mandala, tiling, doolhof, dots_sheet, sums_sheet, letters, POTLOOD, SCHAAR, OUT)
- shapes.py (heart/star/moon/drop/cloud/leaf/fish paden, stencil)
- batch5_kit.py (kp(slug, name, cat, age, diff, draw) voor kleurplaten 200x200, grass, eye, smile)
- batch3.py, batch4.py, batch5.py, batch6.py als voorbeelden van stijl en kwaliteit.

Formaat: viewBox 0 0 200 H (200 voor kleurplaat, 280 voor A4-werkblad). Kleurcodes (één letter per kleurvlak): r rood, o oranje, y geel, l lichtgroen, g groen, t turquoise, b lichtblauw, n blauw, p paars, m roze, k lichtroze, w BRUIN (niet wit!), z grijs, x zwart, "-" = geen kleurnummer (wit).
Categorieën (alleen deze): dieren voertuigen natuur eten ruimte feest wereld patronen boerderij zee dinos sprookjes sport beroepen thuis vormen leren.
Leeftijden: 2-4, 4-6, 6-9, 9+, 12+. Soorten (kind): kleurplaat, knipplaat, bouwplaat, vouwblad, kaart, spel, werkblad, tekenles, sjabloon. difficulty 1-3.
Materialen (slugs): kleurpotloden stiften waskrijtjes kinderschaar lijmstift plakband stevig-papier led-lampionstokje splitpennen potlood elastiek touw verf.
Feestdagen (holiday, optioneel): oudnieuw chinees valentijn carnaval holi suikerfeest pasen koningsdag bevrijding moederdag hemelvaart pinksteren offerfeest vaderdag ketikoti school dierendag halloween divali sintmaarten sinterklaas chanoeka kerst verjaardag.
Niet-kleurplaten hebben i18n.nl.steps nodig (korte, kloppende Nederlandse stappen voor kinderen/ouders). Knip/kaart/sjabloon/bouw: kniplijnen ("cut"); vouwblad: vouwlijnen. Extra pagina's (antwoorden of voorbeeld) via write(..., pages=[("antwoorden"|"extra", "Titel", Sheet)]).

Regels:
- ALLES eigen ontwerp. Geen bekende figuren, merken, personages of nagemaakte bestaande bouwplaten/spellen met merknaam.
- Geen bijna-duplicaten: de bestaande slugs staan in /tmp/slugs.txt. Kies nieuwe onderwerpen/slugs (kebab-case, Nederlands). Varieer.
- Tekst minimaal font-size 4.5; alles binnen het vel; geen tekst als kleurvlak (gebruik outline_text of text).
- Inhoud moet kloppen: sommen/antwoorden correct, bouw-/vouwplaten echt te maken, stappen in de goede volgorde.
- Kwaliteit boven aantal: een tekening die niet herkenbaar of rommelig is, verbeter je of laat je weg.

Werkwijze:
1. Schrijf je generator als scripts/plates/generators/<BESTAND>.py (import uit lib_gen/batch5_kit/shapes; NIET uit batch3/4/5/6 importeren, die schrijven bij import bestanden).
2. Draai: rm -rf <OUTDIR> && OUT=<OUTDIR> python3 <BESTAND>.py (vanuit de generators-map).
3. Render en BEKIJK elk resultaat: node /tmp/claude-0/-home-claude/4a74beb6-26eb-56b6-a053-e7358db067e0/scratchpad/rend.mjs /tmp/claude-0/-home-claude/4a74beb6-26eb-56b6-a053-e7358db067e0/scratchpad/plate.css <png> <svg-bestanden…> (draai vanuit OUTDIR, max ~14 svg's per png), en open de png met de Read-tool. Verbeter wat niet goed is en render opnieuw.
4. NIET ingesten, NIET plates.json aanpassen, NIET committen of pushen, geen andere bestanden in de repo wijzigen behalve je eigen generatorbestand.
5. Rapporteer kort: lijst slugs met soort/leeftijd, wat je hebt weggelaten of twijfelachtig vindt.
