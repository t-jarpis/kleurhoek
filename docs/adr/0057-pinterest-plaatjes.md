# 0057 · Pinterest-plaatjes per plaat

- Status: aangenomen
- Datum: 2026-10-30

## Context
Ouders en leerkrachten zoeken kleurplaten op Pinterest. Elke pin is een link naar de site, en zulke links van andere sites heeft Kleurhoek nodig (ADR 0055).

## Besluit
- **Het plaatje.** De API maakt per plaat en markt een staand plaatje van 1000 × 1500 (`/v1/markets/<markt>/plates/<plaat>/pin.png`) met resvg:
  - de plaat, ingekleurd met de kleuren van "kleuren op nummer";
  - de naam in de taal van de markt;
  - het domein.

  Het domein komt uit een vaste lijst (kleurhoek.nl, .be, .com), zodat er nooit willekeurige tekst op een plaatje komt.
- **Toegang.** De website geeft het plaatje door via `/v1/pins/<markt>/<plaat>.png`. Het CDN mag het een week bewaren.
- **De knop.** Onder de plaat staat "Bewaar op Pinterest" (ShareRow). Dat is een gewone link naar de deelpagina van Pinterest, zonder script of knop van Pinterest zelf, dus zonder tracking. De knop staat alleen op Kleurhoek zelf, niet op de site van een organisatie.

## Gevolgen
- Er is één plaatje per plaat en per markt in het geheugen van de API en in het CDN.
