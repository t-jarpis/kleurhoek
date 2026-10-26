# 0049 · Live markten alleen uit de code, uitzondering heet MARKETS_ONLY

- Status: aangenomen
- Datum: 2026-10-26

## Context
ADR 0044 maakte de code de bron van de live markten, met `MARKETS_OVERRIDE` uit Terraform als uitzondering. Terraform vulde die variabele echter altijd, met de standaardlijst van dat moment. Na ADR 0046 stond op productie daardoor nog de oude lijst van vier markten in de container, en gaven de tien nieuwe markten een 404, tot de volgende `scripts/infra.sh up prod`.

## Besluit
- De website leest alleen nog `MARKETS_ONLY`. Is die leeg, dan beslist `DEFAULT_MARKETS` in de code. `MARKETS_OVERRIDE` en `MARKETS` worden niet meer gelezen, dus een oude waarde in een container doet niets.
- Terraform zet `MARKETS_ONLY` vanuit de nieuwe variabele `markets_only`, standaard leeg. De variabele `markets` blijft alleen voor de rooktests in GitHub.

## Gevolgen
- Een nieuwe markt gaat live met de release zelf, ook op productie, zonder infra-run.
- De oude `MARKETS_OVERRIDE` verdwijnt uit de containers bij de volgende `scripts/infra.sh up`.
