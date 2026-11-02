# 0067 · Sinterklaas in mail en social, Sinterklaasboekje en cadeaulabels met naam

- Status: aangenomen
- Datum: 2026-11-02

## Context
De Sinterklaaskalender (ADR 0065) staat op de site, maar alleen wie hem zelf opzoekt, ziet het deurtje van die dag. Thijs wil een release met wat er nog bij Sinterklaas hoort, voordat de intocht komt (14 november 2026).

## Besluit
- **Eén kalender voor site, social en mail.** Datums en volgorde van de deurtjes staan in `@kleurhoek/catalog-data/calendar` (`sintDates`, `sintDoorSlugs`, `sintDoorOn`). De website, Social en Berichten gebruiken dezelfde functie, zodat ze hetzelfde deurtje noemen.
- **Social.** Op elke dag van de kalender maakt Social een post met het deurtje van die dag (ook op dagen zonder vaste post), met de tekst "nog N nachtjes tot pakjesavond". Alleen voor nl-NL, waar Social nu draait.
- **Mail.** Nieuw onderwerp `sinterklaaskalender`, alleen in nl-NL en nl-BE. De workflow met aanleiding `sint_door` stuurt van de intocht tot pakjesavond elke ochtend om 7 uur de plaat van die dag, per markt. Daarna stopt hij vanzelf; afmelden kan met één klik. Op de kalenderpagina staat een aanmeldformulier met dat onderwerp aan (SubscribeForm met eigen titel en onderwerpen).
- **Sinterklaasboekje.** Op de kalenderpagina een knop per leeftijd die alle Sinterklaasplaten van die leeftijd in het bestaande boekje zet (`/boekje?platen=…`). Een leeftijd met minder dan drie platen gaat op in de leeftijd eronder ("Vanaf 9 jaar").
- **Cadeaulabels en naamkaartjes.** Pagina `/cadeaulabels`, alleen in nl-NL en nl-BE (elders 404). Ouders typen namen en printen een A4 met 8 labels voor de pakjes of 6 naamkaartjes om te vouwen, met tekeningetjes om in te kleuren. Alles gebeurt in de browser: de namen gaan niet naar de server en worden niet bewaard (ADR 0002). Design system: GiftLabels.
- **Taalbanner.** Op pagina's die alleen in het Nederlands bestaan, biedt de taalbanner geen andere taal aan en wijst de taalkeuze onderaan naar de beginpagina van die markt.

## Gevolgen
- Volgend jaar werkt alles vanzelf: de datums worden per jaar berekend.
- Een nieuwe Sinterklaasplaat komt automatisch in kalender, social, mail en boekje.
