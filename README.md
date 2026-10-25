# Kleurhoek

Eigen kleurplaten om online in te kleuren of te printen, met platen per leeftijd, onderwerp, land en feestdag. Start in Nederland, gebouwd om wereldwijd uit te rollen.

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

## Alles lokaal draaien (Docker)
```sh
docker compose up
```
Dat start PostgreSQL, een echte Zitadel, de API, de website en het admin panel. Zitadel wordt automatisch ingericht met dezelfde Terraform-module als dev en prod (`infra/envs/local`), de database krijgt de migraties en alle platen. De eerste keer duurt het een paar minuten (images bouwen).

| Wat | Adres | Inloggen |
| --- | --- | --- |
| Website | http://localhost:3000 | `ouder@kleurhoek.localhost` |
| Admin panel | http://localhost:3002 | `beheerder@kleurhoek.localhost` (wordt vanzelf platformbeheerder) |
| Zitadel-console | http://localhost:8080/ui/console | `zitadel-admin@zitadel.localhost` |

Wachtwoord van alle drie: `Kleurhoek-lokaal-1!`. Dat is alleen lokaal: in productie zijn er geen wachtwoorden. Alles luistert alleen op je eigen machine (127.0.0.1), via http op localhost.

Opnieuw beginnen met een lege database en Zitadel: `docker compose down -v`. Na codewijzigingen: `docker compose up --build`.

## Werken
```sh
pnpm install
pnpm check
```

Zonder Docker en zonder Zitadel: de API draait met een database in het geheugen, de website zonder inlogknop en het admin panel met `ADMIN_DEV_TOKEN` (zie `.env.example`).

Met inloggen: start alleen Zitadel uit compose (`docker compose up zitadel-setup`) en neem de waarden uit het volume `bootstrap` over, of zet de `OIDC_*`-variabelen uit `.env.example`.

De platformpakketten (`@t-jarpis/*`) staan als tarball in `vendor/`; installeren en bouwen werkt zonder token. Bijwerken: zie `vendor/README.md`.

## Architectuur
Zie [docs/architecture.md](docs/architecture.md) en het architectuurdocument: https://claude.ai/artifact/NmTKCWCDF31b6H4RY4XcEQ
