# Architectuur

Het volledige architectuurdocument met diagrammen staat hier: https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ

**Afspraak:** bij elke architectuurwijziging worden het document én de diagrammen bijgewerkt, en komt er een ADR in `docs/adr/`.

## Kort
- Website en admin panel in Next.js, API in NestJS als modulaire monoliet met domeinen: Identiteit en toegang, Catalogus, Lokalisatie, Beschikbaarheid, Analytics (fase 1); Betrokkenheid, Rechten en abonnementen (fase 2); Betalingen (fase 3); Winkel (fase 4).
- Inloggen via Zitadel Cloud, organisatie `Kleurhoek` in de gedeelde instance per omgeving. Gedeelde code uit `t-jarpis/platform`.
- Scaleway Amsterdam (eigen organisatie, een project per omgeving), Cloudflare (eigen zone), PostgreSQL met een schema per domein en row-level security op `tenant_id`.
- Analytics zonder cookies en zonder persoonsgegevens. Accounts alleen voor volwassenen (16+ in NL).
- Kleurhoek is een verkoopbare eenheid: alle data, domeinen en registraties staan apart.
- Website afschermen met een IP-lijst uit het admin panel, gehandhaafd door de website-proxy (ADR 0015).
