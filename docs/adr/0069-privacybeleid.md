# 0069 · Een eigen pagina met het privacybeleid

- Status: aangenomen
- Datum: 2026-11-02

## Context
Pinterest wees de app voor het plaatsen van pins af (trial access). De reden: het privacybeleid moet een eigen, duidelijk zo genoemde pagina zijn. Tot nu toe stond privacy als één alinea in de disclaimer (ADR 0026). Meta vraagt bij de beoordeling van apps hetzelfde.

## Besluit
- **Pagina `/privacy`** in elke markt, met een link in de voettekst naast Disclaimer.
- **Inhoud:**
  - wie we zijn;
  - bezoeken en kleuren, met anonieme telling, geen scripts van anderen, samen kleuren en cadeaulabels;
  - account (alleen 16+), mail en contact;
  - de koppeling met Pinterest, Facebook en Instagram: alleen eigen platen op eigen accounts, sleutels versleuteld, geen gegevens van andere gebruikers;
  - wie ons helpt: Scaleway, Cloudflare, Zitadel en Brevo;
  - je rechten en hoe je klaagt.
- **Talen:** de tekst staat in het Nederlands en het Engels (`apps/web/src/i18n/privacy`). Andere markten krijgen voorlopig de Engelse tekst, met `lang="en"`. Het woord in de voettekst staat wel in alle 29 talen.
- De alinea Privacy in de disclaimer blijft staan.

## Gevolgen
- Verandert er iets aan wat we bewaren, een nieuwe dienst of een nieuwe koppeling, dan passen we deze pagina aan, met de datum bovenaan.
- Vertalingen in de andere 27 talen volgen later, net als bij de disclaimer.
