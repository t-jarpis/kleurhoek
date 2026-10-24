# 0033 · Opbrengst per klik: rapporten van partners inlezen

- Status: aangenomen
- Datum: 2026-10-24

## Context
We tellen doorkliks naar partners (ADR 0011), maar niet wat ze opleveren: verkopen en commissie staan alleen in het partneraccount. Om partners eerlijk te vergelijken is de maatstaf **opbrengst per klik** (commissie ÷ doorkliks): klikratio of conversie alleen zegt maar de helft. Testen met groepen (A/B) volgt later, als er genoeg doorkliks zijn; deze stap is daar de basis voor.

## Besluit
- **Rapport inlezen in het admin panel** (Winkel › Verkopen): een CSV uit het partneraccount (bol, Amazon per land, een netwerk). Kolommen worden herkend aan hun kop (Nederlands, Engels, Duits); de beheerder controleert ze en ziet de eerste rijen voordat hij inleest. De kolomkeuze per partner wordt onthouden.
- **Gegevens**: per verkoopregel datum, sub-ID of tracking-ID, product (ASIN of EAN), aantal, omzet en commissie, in de valuta van het rapport. Opgeteld per dag, sub-ID en product in `shop.sales`; elk ingelezen bestand in `shop.sales_imports`.
- **Herkennen**: het product via de ASIN in de productlink of de EAN; de plaat via de sub-ID die de site zelf meegeeft (`kleurhoek-<plaat>`, alleen als die plaat bestaat). Bij Amazon is er geen sub-ID per klik; daar herkennen we alleen het product.
- **Opnieuw inlezen** van dezelfde partner en periode vervangt de cijfers (bijvoorbeeld na retouren); niets telt dubbel.
- **Overzicht**: tabel "Opbrengst per partner" (doorkliks, verkopen, conversie, commissie, per klik, tot welke dag het rapport loopt; ouder dan 14 dagen = "Rapport verouderd") en "Opbrengst per product". Valuta's worden nooit opgeteld.
- Domeinen blijven gescheiden: verkopen horen bij Winkel, doorkliks bij Analytics; het admin panel legt ze naast elkaar.

## Later
- Rapporten automatisch ophalen zodra een partner dat via een API toestaat.
- Groepen testen: bij de doorklik willekeurig een partner kiezen per bezoekershash, met de groep in de sub-ID, een vooraf vastgestelde stopregel en een melding als een partner niets meer oplevert.
- Voor Amazon per plek een eigen tracking-ID (plaatpagina, thema), zodat ook daar per plek te vergelijken is.

## Gevolgen
- Twee nieuwe tabellen in het schema `shop` (migratie 0019), met de gewone tenant-isolatie.
- Rapporten zijn hooguit 900 kB per keer; exporteer bij veel verkopen een kortere periode.
