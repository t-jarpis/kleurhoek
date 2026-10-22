# Kleurhoek website

```sh
API_URL=http://localhost:3001 DEV_COUNTRY=NL pnpm --filter @kleurhoek/web dev   # http://localhost:3000
```

| Env | Betekenis |
| --- | --- |
| `API_URL` | Basis-URL van de API (server-side) |
| `NEXT_PUBLIC_MARKETS` | Markten die live staan, bijv. `nl-nl,nl-be` |
| `INGEST_KEY` | Sleutel om events bij de API aan te leveren (gelijk aan die van de API) |
| `ANALYTICS_SALT_SECRET` | Geheim voor het dagelijks wisselende zout van de bezoekershash |
| `DEV_COUNTRY` | Alleen lokaal: land als er geen `CF-IPCountry` is |

Zie [ADR 0006](../../docs/adr/0006-website-en-admin.md).
