# 0072 · Dev pauzeren zolang er weinig bezoekers zijn

- Status: aangenomen
- Datum: 2026-11-03
- Vult aan: ADR 0019 en 0021 (dev en prod), ADR 0043 (dev schaalt naar nul)

## Context
Er zijn nog nauwelijks echte bezoekers. Dev kost toch elke maand geld. De containers schalen wel naar nul (ADR 0043), maar de database (DB-DEV-S, circa € 11 per maand plus back-ups) draait altijd. Crawlers op dev.kleurhoek.be en .com maken de containers ook af en toe wakker.

Thijs wil dev uitzetten en weer aanzetten zodra er serieus veel gebruikers zijn.

## Besluit
- **Een pauzeknop voor dev:**
  - `scripts/infra.sh pause dev` zet `paused = true` in `envs/dev/terraform.tfvars` en past Terraform toe.
  - Daarmee verdwijnen de containers, hun eigen domeinen en DNS-records, en de database.
  - Wat blijft staan kost niets of bijna niets: de registry met de laatste images, het netwerk, Zitadel, Cloudflare Access en de zone-instellingen.
- **Weer aan:** `scripts/infra.sh resume dev` zet `paused = false` en draait `up dev`. Dat geeft een nieuwe, lege database en de containers. Daarna rolt het de laatste versie van main uit.
  - De API vult de catalogus bij de eerste start (zoals altijd).
  - Accounts, instellingen en organisaties die alleen op dev stonden, zijn dan weg.
- **Terraform:**
  - De database heeft `count` (`database_enabled` in `modules/scaleway`).
  - `moved`-blokken houden de bestaande databases van dev en prod op hun plek. Zonder die blokken zou Terraform ze vervangen.
  - `modules/site` heeft `paused`: geen apps en geen database.
  - De GitHub-omgeving krijgt `PAUSED`.
- **Uitrollen terwijl dev gepauzeerd is** (repository-variabele `DEV_PAUSED`, gezet door pause/resume):
  - Een push naar main gaat niet naar dev; CI draait wel.
  - Deploy naar prod zonder `ref` neemt de laatste commit op main die door CI kwam, met de unit- en browsertests. Normaal is dat de versie die op dev draait.
  - De samenvatting van de run zegt dat die versie niet eerst op dev stond.
- **Alleen dev.** Productie heeft geen pauzeknop.

## Gevolgen
- Besparing: de database van dev (circa € 11–15 per maand) en de containertijd die crawlers op dev kosten.
- Zolang dev uit staat, gaat een wijziging zonder tussenstap naar productie. De goedkeuring in GitHub blijft, en de rooktest na de uitrol zet bij een fout de vorige versie terug.
  - Een groter of riskant stuk werk: eerst `resume dev`.
- `scripts/infra.sh up dev` weigert zolang dev gepauzeerd is en wijst naar `resume dev`.
- Weer aanzetten duurt circa 15 minuten: een nieuwe database, de containers, certificaten en een uitrol.
