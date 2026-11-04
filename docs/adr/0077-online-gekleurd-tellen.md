# 0077 · Online gekleurd tellen

- Status: aangenomen
- Datum: 2026-11-04

## Context
Op het dashboard stond "Platen ingekleurd". Dat telde alleen `plate_completed`: een plaat die helemaal af is in Kleur op nummer. Gewoon online kleuren, ook als het niet af is, werd wel gemeld (`plate_colored`, bij de eerste kleur of lijn op een plaat per bezoek), maar kwam nergens in de dagtotalen. Thijs had zelf gekleurd en zag dat niet terug.

## Besluit
- **Nieuwe kolom** `colored` in `analytics.daily_totals` (migratie `0031_analytics_colored`). Die telt `plate_colored` per dag, plaat, markt en land.
- **Overzicht en top-platen** geven `colored` naast `completions`.
- **Dashboard:** de kaart heet nu "Online gekleurd" (ook deels), met het aantal "helemaal af met kleur op nummer" eronder.
- **Analytics › Inhoud:** de kaarten "Online gekleurd" en "Af met kleur op nummer", en in de tabel de kolom "Gekleurd". "Gebruikt" telt online gekleurd mee in plaats van alleen af.
- **Aanvullen zonder backfill-script:** `staleDays` geeft ook dagen terug met kleurmeldingen maar nog geen gekleurd-totaal. De uurlijkse telling vult zo vanzelf alle dagen aan waarvan de ruwe events er nog zijn. Een UPDATE in de migratie zou door de row-level security (FORCE) niets doen.

## Gevolgen
- Kleuren van meer dan 90 dagen vóór 4 november 2026 is niet terug te halen; die ruwe events waren al weg (ADR 0002). Sinds ADR 0078 blijven ruwe events bewaard.
- Eén keer per bezoek per plaat: tien keer opnieuw kleuren op dezelfde pagina telt als één.
