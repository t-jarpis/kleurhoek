# 0065 · Sinterklaaskalender en Sinterklaasplaten met Roetveegpiet

- Status: aangenomen
- Datum: 2026-11-01

## Context
In Nederland en Vlaanderen begint het feest al met de intocht, half november. De aftelkalender (ADR 0058) begint pas op 1 december. Thijs wil een eigen Sinterklaaskalender en meer Sinterklaasplaten, voor alle leeftijden en met Piet erbij.

## Besluit
- **Platen.** 15 nieuwe eigen tekeningen (`scripts/plates/generators/batch44_sint.py`, en de 12+-plaat in `batch13e.py` met drie lijndiktes, ADR 0064): van een groot portret voor 2–4 jaar tot de intocht, Pieten op de daken en Sinterklaas als glas-in-lood, plus een mijter om op te zetten (knipplaat). Geen tekst op de platen; namen en stappen in alle 29 talen.
- **Piet** is overal Roetveegpiet: baret met veer, witte kraag, pofbroek en een paar roetvegen op zijn wangen, zoals Thijs koos. Nooit een zwart geschminkt gezicht.
- **Kalender.** Pagina `/sinterklaaskalender`, alleen in nl-NL en nl-BE (andere markten: 404). Een deurtje per dag van de intocht (de eerste zaterdag na 11 november) tot en met pakjesavond: 5 december in Nederland, 6 december in België. In 2026 zijn dat 22 en 23 deurtjes.
  - De eerste deur is de intocht, de laatste pakjesavond, daartussen de Sinterklaasplaten van die markt in een vaste volgorde.
  - Voor de intocht zijn alle deurtjes dicht en telt de kop af naar de intocht. Na pakjesavond en de rest van het jaar staan alle deurtjes van het laatste seizoen open.
  - Het is hetzelfde component als de aftelkalender (`AdventCalendar` met `kind="sint"`, een ander aantal deurtjes en per deur een label met de datum). Deurkleuren rood, goud en paars.
  - De teksten staan in `apps/web/src/lib/sint.ts` en zijn alleen Nederlands, want de pagina bestaat alleen in het Nederlands.
- **Voorpagina.** In nl-NL en nl-BE wijst de banner van 1 november tot en met pakjesavond naar de Sinterklaaskalender, daarna weer naar de aftelkalender.
- **Vindbaarheid.** In de sitemap en `llms.txt` van die twee markten. Paginasoort `sinterklaaskalender` in de eigen telling.

- **Rijker en meer (later op 1 november).** De platen tot 9 jaar kregen meer detail (gestreept pak en knoopjes bij Piet, gouden zoom bij Sint, zadeldek bij het paard, behang, vloer, vlaggetjes en pakjes met stippen) en er kwamen 8 platen voor jonge kinderen bij: 23 nieuwe Sinterklaasplaten in totaal. De seed maakt nu ook een nieuwe versie als het aantal vlakken verandert; opgeslagen kleurwerk blijft bij zijn eigen versie.

## Gevolgen
- Volgend jaar schuift alles vanzelf mee: de intocht en het aantal deurtjes worden per jaar berekend.
- Valt de echte intocht een keer anders, dan passen we alleen `intocht()` aan.
- Social (ADR 0063) maakt nog geen posts over de deurtjes van deze kalender, alleen over de aftelkalender in december.
