# Kleurhoek

Zelf getekende kleurplaten om online in te kleuren of te printen, met platen per leeftijd, onderwerp, land en feestdag. Start in Nederland, gebouwd om wereldwijd uit te rollen.

## Indeling
| Map | Inhoud |
| --- | --- |
| `apps/web` | Publieke website (Next.js), volgt in fase 1 |
| `apps/admin` | Admin panel (Next.js), volgt in fase 1 |
| `apps/api` | API (NestJS, modulaire monoliet), volgt in fase 1 |
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

## Architectuur
Zie [docs/architecture.md](docs/architecture.md) en het architectuurdocument: https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ
