# 0070 · Platen in kleur in het raster

- Status: aangenomen
- Datum: 2026-11-02

## Context
Het platenraster toonde alleen lijntekeningen. Een proef met ingekleurde platen zag er veel vrolijker uit en sluit aan bij wat bezoekers van Pinterest gewend zijn. Een ouder die snel wil printen, wil soms juist de lege plaat zien. Thijs koos voor een schakelaar, standaard aan.

## Besluit
- **Ingekleurd bestand.** De API serveert naast `<versie>[.<taal>-<hash>].svg` ook `.kleur.svg`: dezelfde plaat met de vlakken in de kleuren van kleur-op-nummer (`colorIn`, net als de Pinterest-plaatjes, ADR 0057). Per versie onveranderlijk, dus het CDN bewaart het. De website laat dat bestand door via `/v1/assets`.
- **Schakelaar "In kleur"** (design system: ColorPreview) rechts boven het raster op de voorpagina en de onderwerppagina's.
  - Standaard aan. De keuze blijft op het apparaat in `localStorage` (`kh:inkleur`), zonder cookie.
  - De keuze geldt meteen voor elk raster op de site.
  - Het woord staat in alle 29 talen.
- **Altijd lijnen:** de kleurstudio, printen, het boekje, mail en de deelplaatjes veranderen niet.

## Gevolgen
- Wie de keuze uit heeft gezet, ziet bij het laden heel even de ingekleurde versie, omdat de server niet weet wat er op het apparaat staat. Dat nemen we voor lief; een cookie willen we niet.
- Een plaat zonder kleuren voor kleur-op-nummer blijft in het raster gewoon een lijntekening.
