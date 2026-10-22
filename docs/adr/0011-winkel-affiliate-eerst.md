# 0011 · Winkel: eerst doorverwijzen (affiliate), gericht op ouders

- Status: aangenomen
- Datum: 2026-10-22

## Context
De site moet spullen kunnen aanbieden (potloden, scharen, lijm) zonder inkoop, met snelle levering, en in meerdere landen. Later wil de eigenaar misschien zelf gaan leveren, maar alleen voor producten waarvan bewezen is dat ouders ze willen. Kinderen gebruiken de site; reclame die kinderen bereikt is aan strenge regels gebonden (ACM: commerciële bedoeling duidelijk, niet aansporen tot kopen, niet profileren).

## Besluit
- **Domein Winkel (`shop`) begint met doorverwijzen.** Partners (bol, Amazon per land, winkels via netwerken als Daisycon of Awin, of een winkel zonder programma), producten, en welk product bij welk materiaal hoort. Per markt en per materiaal wint het product met de laagste voorkeur.
- **De koppeling staat in het admin panel.** Per partner een sjabloon met `{url}` (productpagina), `{subId}` (de plaat waar de klik vandaan kwam) en eigen velden zoals `{siteId}` of `{tag}`. Eigen partners toevoegen kan ook. Een partner staat uit tot alle velden zijn ingevuld. Elke wijziging komt in het auditlog. Rechten: `shop.read`, `shop.manage`.
- **Geen open doorverwijzing.** De route `/ga/<product>` op de website vraagt het adres op bij de API, die het alleen bouwt uit opgeslagen gegevens; productpagina's moeten https zijn en op de domeinen van de partner staan.
- **Alleen voor ouders.** Producten staan alleen in het blok "Voor ouders" onder de studio, met de tekst dat het partnerlinks zijn en `rel="sponsored nofollow"`. Nooit in de kleurstudio, nooit in de platen, nooit gericht op kinderen, geen profilering.
- **Meten zonder cookies.** `materials_view` (het blok was echt in beeld) en `product_click` (via `/ga`) gaan langs dezelfde weg als de andere analytics: land, apparaat en een dagelijkse bezoekershash. Dagtotalen per product, plaat, markt en land. Het admin panel toont doorkliks, klikratio, cijfers per partner en per plaat, en **kandidaten om zelf te leveren** (minstens 20 bezoekers in de periode, niet dalend).
- **Verkopen meten we niet zelf**: die staan in het partneraccount, terug te vinden per plaat via de sub-ID.

## Volgende stappen
- Producten zoeken en importeren uit productfeeds (bol, Daisycon) in plaats van met de hand invoeren.
- Verkopen uit partnerrapportages importeren, zodat het admin panel ook omzet per product toont.
- Zelf leveren (eigen pakket, fulfilmentpartner) als nieuw onderdeel van dit domein, met betalingen in het domein Betalingen.
