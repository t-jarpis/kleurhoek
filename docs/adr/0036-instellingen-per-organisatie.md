# 0036 · Instellingen per organisatie: leerdoelen, collecties en zelf beheren

- Status: aangenomen
- Datum: 2026-10-25

## Context
Scholen, bso's en bibliotheken willen meer sturing dan onderwerp, leeftijd en soort (ADR 0017): educatieve filters, een vaste selectie platen, en losse platen weg kunnen laten, het liefst zonder Kleurhoek te hoeven mailen.

## Besluit
- **Leerdoelen** zijn een vaste lijst van negen algemene doelen (rekenen, taal, fijne motoriek, knutselen, vormen/ruimte/logica, tekenen, wereld en natuur, feestdagen en seizoenen, samen spelen). Ze worden **afgeleid**, niet ingevoerd: uit soort, onderwerp, feestdag, wereld en de naam van de plaat (`packages/catalog-data/goals.js`), met uitzonderingen per plaat in `goals-overrides.json`. Elke nieuwe plaat krijgt ze vanzelf; een test bewaakt dat elke plaat er minstens één heeft. Namen per taal staan in hetzelfde bestand.
- **Collecties** horen bij het domein Catalogus (`catalog.collections`): een code, naam en omschrijving per taal en platen op volgorde. Beheer in het admin panel (Inhoud › Collecties, recht `catalog.manage`). Een collectie die een organisatie gebruikt kan niet worden verwijderd.
- **Aanbod van een organisatie** krijgt drie velden: `collections` (alleen platen uit deze collecties; null = alles), `goals` (alleen platen met minstens één van deze leerdoelen; null = alles) en `excluded` (losse platen uit). De regel staat op één plek (`organizations/offer.ts`, `offerAllows`); Storefront haalt de platen van de collecties bij Catalogus op.
- **Filter Leerdoel** op de site is een functie per organisatie (`features.learningFilters`), standaard aan voor scholen en opvang. Kleurhoek zelf toont het niet.
- **Zelf beheren**: een organisatie heeft beheerders (`organizations.managers`). Dat zijn gewone websiteaccounts, geen beheeraccounts (ADR 0018): de persoon logt één keer in op de site van de organisatie en Kleurhoek voegt hem toe op e-mailadres (Organisaties › Beheerders). Op de site staat dan onderaan "Beheer" (`/<markt>/beheer`, noindex): leerdoelen, collecties en losse platen aan of uit (design system: OfferEditor). Onderwerpen, leeftijden, soort, markten, huisstijl en functies blijven bij Kleurhoek. De API (`/v1/me/organizations`) controleert bij elk verzoek dat het account beheerder is van die organisatie; de website stuurt alles via de eigen `/auth`-routes, het token komt niet in de browser. Na opslaan vervalt de cache van die organisatie meteen.
- Een verwijderd account verdwijnt ook als beheerder (privacy, ADR 0002).

## Gevolgen
- Migratie 0021: tabellen `catalog.collections` en `organizations.managers`, met RLS. Oude aanbod-rijen werken zonder migratie (ontbrekende velden = alles).
- Leerdoelen zijn een benadering op basis van naam en soort, geen curriculumkoppeling. Fouten corrigeren we in `goals-overrides.json`.
- Inloggen via de eigen schoolomgeving (SSO) volgt later en verandert niets aan dit model: een beheerder blijft een account op de site.
