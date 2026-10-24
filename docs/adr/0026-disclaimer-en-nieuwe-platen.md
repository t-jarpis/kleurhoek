# 0026 Disclaimer, voettekst en platen toevoegen met scripts

Datum: 24-10-2026. Status: aangenomen.

## Context
Vergelijkbare sites hebben een disclaimer; Kleurhoek had er geen, en ook geen vaste plek voor contact. Daarnaast groeit de catalogus flink (doel 300 platen na een jaar, ADR 0022) en moeten nieuwe platen snel en foutloos toegevoegd kunnen worden.

## Besluit
- **Disclaimer** op `/{markt}/disclaimer`: eigen tekeningen en wat je ermee mag (gratis thuis, school, opvang; niet verkopen of herpubliceren), de Bronnengids (alleen links, geen beeld, dagelijkse controle, maker kan link laten aanpassen), merken, partnerlinks, auteursrecht melden (via contact, reactie binnen 5 werkdagen), veilig knutselen, aansprakelijkheid, privacy in het kort, Nederlands recht.
- **Voettekst** (`SiteFooter`) op elke websitepagina met Thema's bij de maker, Contact en Disclaimer.
- **Platen toevoegen** gaat met `scripts/plates/`:
  - `preview.mjs <map> <uit.png>`: contactvel met lege plaat, nummers en ingekleurde versie, plus controles (aantal vlakken en kleurcodes, vlakken die helemaal bedekt zijn).
  - `ingest.mjs <map>`: nummert de vlakken, berekent de posities voor kleur-op-nummer in een echte browser (hetzelfde algoritme als het prototype) en schrijft `plates/*.svg` en `plates.json`.
  - Een concept is `<slug>.svg` + `<slug>.json` (zie de uitleg in `ingest.mjs`).
- Nieuwe categorieën: boerderij, onder water, dino's, sprookjes, sport en spel, beroepen, thuis en speelgoed, vormen en figuren.

## Gevolgen
- Nieuwe platen komen bij de volgende start van de API in de database (seed is idempotent, ADR 0021).
- De disclaimer is Nederlandstalig; andere markten krijgen een eigen versie als ze live gaan. Bedrijfsgegevens (KvK) aanvullen zodra die er zijn.
