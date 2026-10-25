# 0044 · Engels voor het Verenigd Koninkrijk (en-GB)

- Status: aangenomen
- Datum: 2026-10-25

## Context
Na Nederland en België (ADR 0040) is Engels de taal met het grootste bereik. Er komen al bezoekers uit landen waarvoor we geen markt hebben, en Engels is voor veel van hen de tweede browsertaal. De websiteteksten bestonden al in Brits Engels; de platen nog niet.

## Besluit
- **Markt en-GB:** live op kleurhoek.com/en-gb (Verenigd Koninkrijk, A4). Een account mag vanaf 13 jaar (UK GDPR).
- **Taalkeuze:** wie op kleurhoek.com binnenkomt met Engels als eerste browsertaal, of als eerste taal die we hebben, gaat naar en-GB. Bijvoorbeeld een Finse browser met Engels als tweede taal. In de taalkeuze onderaan heet de markt "United Kingdom".
- **Feestdagen GB:**
  - Wel: Oud en nieuw, Chinees Nieuwjaar, Valentijn, Holi, Suikerfeest, Pasen, Offerfeest, Vaderdag, Halloween, Divali, Chanoeka, Kerst.
  - Moederdag valt op Mothering Sunday (vierde zondag van de vastentijd).
  - De eerste schooldag is begin september.
  - Nieuw: Bonfire Night (5 november).
  - Niet: Carnaval, Koningsdag, Bevrijdingsdag, Hemelvaart, Pinksteren, Keti Koti, Sint-Maarten, Sinterklaas en Dierendag. De platen daarvan zijn in de Britse markt niet te zien.
- **Vertaling:** alle platen die niet taalgebonden zijn, plus de woordenlijst van de teksten in platen, zijn in het Engels. `check-lang.mjs en` controleert of alles op het vel past.

## Gevolgen
- `MARKETS` staat standaard op `nl-nl,nl-be,fr-be,en-gb` (website-code en Terraform). Op dev en prod is en-GB pas zichtbaar na `scripts/infra.sh up dev` en `up prod`, omdat Terraform `MARKETS` daar expliciet zet.
