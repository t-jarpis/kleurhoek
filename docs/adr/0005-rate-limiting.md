# 0005 · Rate limiting in twee lagen, instelbaar in het admin panel

- Status: aangenomen
- Datum: 2026-10-22

## Besluit
- **Cloudflare (rand):** grove limieten per IP tegen bots en DDoS, beheerd in Terraform. Volgt met de infrastructuur in fase 1.
- **API (fijnmazig):** regels per soort verkeer (`public-read`, `assets`, `events-ingest`, `admin`, `api-default`). Endpoints kiezen hun regel met `@RateLimit('<regel>')`.
- Sleutels zijn gehasht (tenant + IP, gebruiker of client): geen ruwe IP-adressen in geheugen of Redis.
- Antwoorden dragen de headers `RateLimit` en `RateLimit-Policy`; boven de limiet volgt 429 met `Retry-After`.
- Regels staan in `operations.rate_limits` en zijn in het admin panel te bekijken (`operations.ratelimit.read`) en te wijzigen (`operations.ratelimit.manage`). Wijzigingen werken binnen 30 seconden en komen in het auditlog, in dezelfde transactie.
- Doorgelaten en geblokkeerde verzoeken worden per dag en regel geteld (`operations.rate_limit_stats`).

## Gevolgen
- Met meer dan één API-replica moet de teller gedeeld worden: dan komt een Redis-store achter `RateLimitStore`. Tot die tijd telt elke replica apart.
- Admin-verzoeken worden tot de koppeling met Zitadel per IP geteld in plaats van per gebruiker.
