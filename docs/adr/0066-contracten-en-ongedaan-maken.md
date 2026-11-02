# 0066 · Contract per domein, events als richting, en ongedaan maken

- Status: aangenomen
- Datum: 2026-11-02

## Context
Thijs las over Open Mercato, een TypeScript-framework met modules die steeds dezelfde vorm hebben, een machineleesbaar contract per module, events tussen modules en commands met audit en ongedaan maken. Veel daarvan doet Kleurhoek al: monorepo, een schema per domein met row-level security (ADR 0001), rechten per functie en een auditlog. Wat ontbrak, was een vastgelegd contract per domein en de mogelijkheid om een wijziging terug te zetten.

## Besluit
- **Contract per domein.** Elk domein in `apps/api/src/modules/<domein>/` heeft een `AGENTS.md` met:
  - wat het domein doet;
  - zijn schema en endpoints;
  - de lijst **Publiek**: de enige bestanden die andere domeinen mogen importeren.

  Het bestand is voor mensen en voor AI-assistenten. Bijna alles bleek al via services te lopen. Eén type-import uit het schema van Organisaties loopt nu via `organizations/offer.ts`.
- **Controle.** `test/boundaries.test.ts` faalt als een domein iets van een ander domein importeert dat daar niet als publiek staat. Zo loopt het mee in `pnpm check`.
- **Events als richting.** Nieuwe koppelingen tussen domeinen liefst als domeinevent in plaats van een directe aanroep. We bouwen dat stap voor stap in bij de volgende wijziging die erom vraagt, niet in één keer. Het contract heeft er al een kopje voor.
- **Ongedaan maken.** Het bestaande auditlog legt al vast wat er voor en na een wijziging was. Daarop bouwen we:
  - Een domein meldt bij `UndoRegistry` (Identity) per auditactie hoe hij de oude toestand terugzet, met welk recht en onder welk label.
  - Identity bewaakt de regels:
    - alleen de laatste wijziging van iets kan terug;
    - je hebt het recht van dat domein nodig;
    - het terugzetten gebeurt in één transactie en komt zelf ook in het auditlog, als `undo:<actie>`.
  - Het auditlog blijft alleen-toevoegen: de app mag er niets in wijzigen of uit verwijderen.
  - Eerst vier acties:
    - vindbaarheid (`seo.update`, `seo.defaults`);
    - rate limits;
    - winkelkoppelingen;
    - doelen.
- **Admin panel.** Een nieuwe pagina Wijzigingen (design system: ChangeLog) toont de laatste wijzigingen met wie, wat, waarop en voor en na, en een knop Terugzetten waar dat mag. Er is een nieuwe permissie `audit.read`, voor platformbeheerders en contentbeheerders.

## Niet overgenomen
- **Overlays en services vervangen via dependency injection:** dat is bedoeld voor een framework dat anderen aanpassen; organisaties hebben instellingen (ADR 0036).
- **Een visuele workflow-designer:** de mail-workflows hebben al stappen.
- **Vectorzoeken:** bij ruim 1.000 platen is het niet nodig.

## Gevolgen
- Een nieuwe import tussen domeinen betekent ook het contract bijwerken. De test wijst erop.
- Nieuwe wijzigbare instellingen kunnen terugzetten aanbieden met een paar regels in hun domein.
