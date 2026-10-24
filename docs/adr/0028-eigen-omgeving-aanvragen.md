# 0028 Eigen omgeving aanvragen

Datum: 24-10-2026. Status: aangenomen.

## Context
Organisaties (scholen, opvang, verenigingen, bedrijven) kunnen al een eigen versie van Kleurhoek krijgen (ADR 0017), maar bezoekers wisten dat niet en konden het nergens aanvragen.

## Besluit
- Pagina **Eigen omgeving** op `/{markt}/eigen-omgeving`, alleen op Kleurhoek zelf (op de site van een organisatie: 404). Uitleg van wat je krijgt, gebaseerd op wat ADR 0017 echt biedt: eigen adres (`{code}.kleurhoek.nl`, eigen domein op aanvraag), huisstijl, eigen aanbod, webshop en partnerlinks uit, geen tracking en niet in Google, nieuwe platen vanzelf. Geen prijzen op de pagina; die bespreken we in het antwoord.
- Link in de voettekst (alleen op Kleurhoek zelf) en een verwijzing op de contactpagina.
- **Aanvraagformulier**: naam en soort organisatie, gewenst adres (voorstel uit de naam), aantal kinderen, website, contactpersoon, e-mail en wens. Het gaat via het domein Contact (ADR 0024) als gesprek met onderwerp `organization`; de gegevens van de organisatie staan in de nieuwe kolom `contact.conversations.details` (migratie 0017). Zelfde spambescherming en rate limit als het contactformulier.
- In de **inbox** staat de aanvraag als tabel, met de knop *Organisatie aanmaken*: die opent Organisaties met naam, code en soort al ingevuld (alleen met `organizations.manage`).

## Gevolgen
- Een aanvraag valt onder dezelfde bewaartermijn als andere berichten (12 maanden na het laatste bericht).
- Later kan de aanvraag automatisch een concept-organisatie aanmaken; nu blijft het een bewuste stap van een beheerder.
