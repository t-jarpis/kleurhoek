# 0080 · Pagina Wat is er nieuw, en een hoofdgebied op elke pagina

- Status: aangenomen
- Datum: 2026-11-04

## Context
De Public-notes (ADR 0030) stonden alleen in het admin panel. Bezoekers en zoekmachines zagen niet wat er nieuw was. Verder misten veel pagina's een hoofdgebied (`<main>`) voor schermlezers. En een onbekend adres binnen een markt gaf de kale 404 van Next, zonder taal op `<html>`.

## Besluit
- **Pagina `/nieuw`** in elke markt, met een link in de voettekst.
  - Bovenaan de nieuwste platen die in die markt te zien zijn, nieuwste eerst, hooguit 36. Ze komen uit het nieuwe endpoint `GET /v1/markets/:market/new` (Etalage) en volgen de schakelaar In kleur.
  - In nl-NL en nl-BE, op Kleurhoek zelf, staat daaronder "Nieuw op de site": de Public-notes per uitrol, nieuwste eerst, zonder herhalingen, uit het publieke endpoint `GET /v1/news` (Beheer). Die teksten zijn Nederlands, daarom alleen daar.
  - Titel en inleiding staan in alle 29 talen. De pagina staat in de sitemap en `llms.txt`, met het paginasoort `nieuw` in de telling.
- **Hoofdgebied:** elke pagina heeft nu precies één `<main>`.
- **Onbekende adressen:** `[org]/[market]/[...rest]` geeft de 404 van de markt, binnen de layout van die markt (taal, voettekst, hoofdgebied).

## Gevolgen
- Een Public-note in een commit verschijnt na de uitrol vanzelf op de pagina in het Nederlands. Wat daar staat, moet voor bezoekers geschreven zijn.
- Vertaalde nieuwsberichten komen pas als er vraag naar is.
