# Kleurhoek API

NestJS (Fastify) als modulaire monoliet. Domeinen in `src/modules`, elk met een eigen PostgreSQL-schema.

| Module | Rol |
| --- | --- |
| `catalog` | Platen, versies (SVG + kleur-op-nummer), categorieën, leeftijden, werelddelen |
| `localization` | Markten (land + taal) en vertalingen |
| `availability` | Zichtbaarheid per land, feestdagen en seizoenen |
| `analytics` | Events van de Cloudflare Worker, dagtotalen, samenvatting voor het admin panel |
| `operations` | Rate limits (instelbaar in het admin panel) |
| `identity` | Admin-toegang (deny-by-default tot Zitadel gekoppeld is) en auditlog |
| `storefront` | Leesmodel voor de website: combineert catalogus, lokalisatie en beschikbaarheid |

## Lokaal
```sh
pnpm --filter @kleurhoek/api dev     # zonder DATABASE_URL: PostgreSQL in het geheugen met alle 65 platen
curl localhost:3001/v1/markets/nl-NL/plates
```

## Database
- Migraties in `drizzle/`. Nieuwe migratie: `pnpm --filter @kleurhoek/api db:generate`.
- Row-level security op `tenant_id`; de app draait per transactie als rol `app_user` (zie `src/db/tenant.ts`).

## Endpoints
| Methode | Pad | Toegang |
| --- | --- | --- |
| GET | `/health` | publiek |
| GET | `/v1/markets/:market/plates` | publiek, filters `category`, `age`, `continent`, `country`, `holiday` |
| GET | `/v1/markets/:market/plates/:slug` | publiek |
| GET | `/v1/markets/:market/taxonomy` | publiek |
| GET | `/v1/markets/:market/season` | publiek |
| GET | `/v1/assets/plates/:slug/:version.svg` | publiek, cache voor altijd |
| POST | `/v1/internal/events` | alleen Cloudflare Worker (`x-ingest-key`) |
| GET | `/v1/admin/analytics/summary` | `analytics.read` |
| GET | `/v1/admin/rate-limits` | `operations.ratelimit.read` |
| PUT | `/v1/admin/rate-limits/:slug` | `operations.ratelimit.manage` |
