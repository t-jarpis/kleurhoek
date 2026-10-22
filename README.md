# Kleurhoek

Zelf getekende kleurplaten om online in te kleuren of te printen, met platen per leeftijd, onderwerp, land en feestdag. Start in Nederland, gebouwd om wereldwijd uit te rollen.

## Indeling
| Map | Inhoud |
| --- | --- |
| `apps/web` | Publieke website (Next.js) |
| `apps/admin` | Admin panel (Next.js): dashboard, gebruikers en rollen, rate limits |
| `apps/api` | API (NestJS, modulaire monoliet) |
| `packages/` | Domeinpakketten van Kleurhoek |
| `infra/` | Terraform voor de omgevingen van Kleurhoek, volgt in fase 1 |
| `prototype/` | Het eerste ontwerp, referentie voor de migratie |
| `docs/` | Architectuur en beslissingen (ADR's) |

Gedeelde bouwstenen komen uit [`t-jarpis/platform`](https://github.com/t-jarpis/platform) als `@t-jarpis/*`-pakketten.

## Werken
```sh
pnpm install
pnpm check
```

Lokaal zonder Zitadel: de API draait met een database in het geheugen, de website zonder inlogknop en het admin panel met `ADMIN_DEV_TOKEN` (zie `.env.example`).

Met inloggen: zet de `OIDC_*`-variabelen uit `.env.example`. Voor een test zonder echte Zitadel start je de nep-Zitadel uit `@t-jarpis/auth/testing`; die keurt elke login direct goed.

`@t-jarpis/auth` komt tijdelijk uit een lokale map (`file:../../../platform/...`). Zodra het platform gepubliceerd is, wordt dat `^0.2.0` uit GitHub Packages.

## Architectuur
Zie [docs/architecture.md](docs/architecture.md) en het architectuurdocument: https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ
