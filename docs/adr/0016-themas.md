# 0016 · Thema's: een andere stijl zonder herbouw

- Status: aangenomen; deels vervangen door 0017 (alle thema's in één CSS, keuze per organisatie)
- Datum: 2026-10-23

## Aanleiding
De stijl Studio (ADR 0012) moest in de code komen. De eigenaar wil later een andere stijl kunnen kiezen zonder de hele website en het admin panel opnieuw te bouwen.

## Besluit
Drie lagen. Alleen de onderste verschilt per stijl.

1. **Thema** (`packages/theme/themes/<naam>/`):
   - `tokens.json`, rechtstreeks uit het design system. Daarin staan kleuren (licht en donker), typografie, ruimte, radii, schaduwen en modi, plus de groep *knoppen*: stijlkeuzes die geen kleur of maat zijn, zoals het displayfont, de hoek van knoppen en chips, de dikte van randen, de kleur van een gekozen filter en het hover-effect van kaarten.
   - `theme.json`, met het logo (woord en blokjes) en het standaardlettertype.
2. **Componenten** (`packages/theme/src/ui.css` en de app-CSS): lezen alleen semantische variabelen (`--color-text`, `--radius-control`, `--chip-selected-bg` …), nooit een kleur of font. `pnpm check` faalt op een losse hex-waarde in `apps/web` of `apps/admin` (`scripts/check-hex.mjs`; uitzondering met `theme-allow`, bijvoorbeeld de krijtkleuren van de studio, want dat is inhoud).
3. **Apps**: importeren `@kleurhoek/theme/theme.css` en `ui.css`, en het logo uit `@kleurhoek/theme`. De modus (kind, ouder, beheer) zit op `data-mode`; licht en donker volgen het systeem, met `data-theme` om te forceren.

**Lettertypen** staan los van het thema in `packages/theme/fonts/<naam>/` (woff2-bestanden plus `font.json`). Nu beschikbaar: Manrope (standaard bij Studio) en Nunito, allebei onder de SIL Open Font License. Wisselen kan in `theme.config.json` (`"font": "nunito"`) of met `KLEURHOEK_FONT`.

`scripts/build.mjs` zet het actieve thema (`theme.config.json` of `KLEURHOEK_THEME`) om naar `generated/theme.css` en `generated/theme.ts`. Die staan in git; de test controleert dat ze actueel zijn.

**Een nieuwe stijl** is daarmee: in het design system de nieuwe tokens en knoppen vastleggen (regel van ADR 0012), de `tokens.json` daarvan in een map `themes/<naam>` zetten met de fonts en een `theme.json`, `theme.config.json` aanpassen en `pnpm --filter @kleurhoek/theme build`. Componenten blijven hetzelfde, behalve als de nieuwe stijl iets wil dat nog geen knop heeft. Dan komt er een knop bij, met de huidige waarde in Studio.

## Afwegingen
- *Eén thema per build* in plaats van wisselen in de browser: eenvoudiger en sneller, en een merk wisselt niet per bezoeker. Wisselen per bezoeker kan later met meerdere `[data-theme]`-blokken uit hetzelfde script.
- *Gegenereerde bestanden in git*: lokaal draaien en de Docker-build hebben geen extra stap nodig.
- *Nog in de kleurhoek-repo*: het thema-pakket verhuist pas naar het platform als een tweede site het nodig heeft (platform ADR 0001). De opzet (tokens → CSS-variabelen → componenten) is daar al op voorbereid.
