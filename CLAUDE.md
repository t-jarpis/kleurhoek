# Kleurhoek – werkafspraken

- Communiceer met Thijs in het Nederlands. Code, identifiers en commits in het Engels, documentatie en UI-teksten in het Nederlands (plus vertalingen).
- **Architectuur bijhouden:** bij elke architectuurwijziging het architectuurdocument én de diagrammen bijwerken (https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ) en een ADR toevoegen in `docs/adr/`.
- Gedeelde code komt uit `@t-jarpis/*` (repo `t-jarpis/platform`). Kleurhoek-code gaat nooit naar het platform; iets verhuist pas als een tweede site het nodig heeft (platform ADR 0001).
- Domeinen hebben harde grenzen (ADR 0001): eigen schema, geen imports van andermans internals.
- **Design system eerst** (ADR 0012): een nieuwe of gewijzigde component, variant of staat komt eerst in het design system (https://claude.ai/artifact/L7Df2x1wNxdihbVvuKuRMt: spec, tokens, preview) en wordt pas daarna gebouwd. Geen losse hex-waarden of maten in componenten.
- Alle platen zijn eigen tekeningen. Geen bekende figuren, merken of werk van anderen.
- Privacy: geen tracking-cookies, geen persoonsgegevens in analytics, kinderen zonder account (ADR 0002).
- Alles in deze repo moet overdraagbaar zijn bij verkoop (ADR 0004). Geen geheimen of `.env`-bestanden committen.
- Platformpakketten staan als tarball in `vendor/` (ADR 0009); bijwerken met `scripts/platform-update.mjs`, nooit met de hand.
- `docker compose up` moet altijd zonder handwerk een werkende omgeving geven, inclusief inloggen via de echte Zitadel. Raak je login, env-variabelen of Terraform aan, test dan ook compose.
- Voor een commit: `pnpm check` groen.
