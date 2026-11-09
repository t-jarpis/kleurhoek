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

## Addendum (9 november 2026): de eigen website telt niet mee voor leesverzoeken
Sinds ISR (ADR 0093) haalt de website pagina-data server-side op, zonder `CF-Connecting-IP`. Al die verzoeken kwamen van één socket-adres en vielen onder `public-read` (300 per minuut). Toen zoekmachines veel nog niet gecachte pagina's tegelijk opvroegen, gaf de API 429 en de website 500 (Search Console: "Server error (5xx)" op kleurhoek.be). Voor `public-read` en `assets` geldt de limiet nu alleen voor verzoeken met `CF-Connecting-IP` (bezoekers via Cloudflare); server-side ophalen door de eigen website wordt niet beperkt. De API heeft geen publieke ingang, dus zonder die header is de afzender altijd een van onze eigen servers.
