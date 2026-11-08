# 0095 · Denkhoek in het Scaleway-project van Kleurhoek

- Status: aangenomen
- Datum: 2026-11-08

## Context
Denkhoek (eigen repo `t-jarpis/denkhoek`) heeft voor bezoekerscijfers en beheer een database nodig. Thijs koos voor geen extra kosten: een eigen database op de Postgres-server van Kleurhoek. Scaleway kan niet tussen projecten routeren, dus Denkhoek draait in het project `kleurhoek-prod` (Denkhoek ADR 0006).

## Besluit
- Denkhoek heeft in `kleurhoek-prod` een eigen container-namespace, registry en containers, aan het privénetwerk van Kleurhoek. Op de RDB-instance van Kleurhoek staat een eigen database `denkhoek` met een eigen gebruiker zonder adminrechten, alleen met rechten op die database.
- Alles van Denkhoek staat in de Terraform-state van Denkhoek. Het privénetwerk en de instance van Kleurhoek worden daar alleen op naam opgezocht. In de Terraform van Kleurhoek verandert niets.
- **Niet hernoemen of vervangen zonder Denkhoek mee te nemen:** het privénetwerk en de RDB-instance van Kleurhoek-prod. Een herstart of storing van de database raakt beide sites.

## Gevolgen
- Kleurhoek blijft los verkoopbaar: bij verkoop van een van beide verhuist Denkhoek met `pg_dump`/restore naar een eigen project (draaiboek in Denkhoek ADR 0006).
- De deploy-sleutel van Denkhoek heeft rechten op het project `kleurhoek-prod`. De Deploy-workflow van Denkhoek werkt alleen containers in de eigen namespace bij, en elke uitrol vraagt goedkeuring.
