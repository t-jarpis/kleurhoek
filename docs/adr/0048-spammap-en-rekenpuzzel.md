# 0048 · Contactformulier: spammap en onzichtbare rekenpuzzel, geen captcha

- Status: aangenomen
- Datum: 2026-10-26

## Context
Het contactformulier heeft een verborgen veld, een minimale invultijd en een limiet per IP-adres (ADR 0024). Toch kwam er een SEO-verkoopbericht binnen ("Hey team kleurhoek.com"). Zulke berichten komen van mensen of van programma's die een echte browser bedienen. Een captcha houdt die niet tegen: captcha's worden voor een paar cent door mensen opgelost. Voor bezoekers en kinderen is een captcha bovendien vervelend, en een externe dienst als reCAPTCHA past niet bij de privacyafspraken (ADR 0002).

## Besluit
- **Spammap.** De API geeft elk bericht een score (`contact/spam.ts`). Punten zijn er voor:
  - verkooppraat: SEO, Google-ranking, backlinks, offerte of prijslijst, marketing;
  - de domeinnaam als aanhef;
  - links in het bericht of als naam;
  - een ontbrekende of ongeldige rekenpuzzel.

  Vanaf score 3 krijgt het gesprek de status `spam`. Er komt geen melding van, en het telt niet mee in Nieuw of Alles. De reden staat erbij als interne notitie. In het admin panel staat Spam als eigen tab, met "Geen spam: terug naar de inbox" en "Markeer als spam". Spam wordt na 30 dagen verwijderd; de rest pas na 12 maanden. Er wordt niets weggegooid zonder dat je het kunt zien.
- **Onzichtbare rekenpuzzel (proof-of-work).** Een formulier haalt via de website een opgave op bij `GET /v1/contact/challenge`: vind n met sha256(salt + n) = challenge, waarbij n hooguit 20.000 is. De browser lost die op de achtergrond op, meestal in minder dan een seconde, en stuurt de oplossing mee in een verborgen veld.
  - De opgave is ondertekend met een HMAC (afgeleid van `INGEST_KEY`), verloopt na een uur en is per instance één keer bruikbaar.
  - Er is geen externe dienst en er zijn geen cookies.
  - Dit geldt voor het contactformulier en voor de aanvraag van een eigen omgeving.
- De bestaande drie verdedigingen blijven: verborgen veld, minimale invultijd en rate limit. Wat daarop afketst, wordt nog steeds stil weggegooid.

## Gevolgen
- Een bezoeker zonder JavaScript kan nog steeds een bericht sturen; dat bericht komt in Spam. Kijk daar dus af en toe.
- Wie veel formulieren verstuurt, moet per formulier rekenen. Massaal versturen wordt daardoor duur en traag.
- De lijst met woorden voor de score staat in code. Komt er nieuw soort spam door, dan breid je die lijst uit.
