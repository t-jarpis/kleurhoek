# 0015 · Website afschermen met een IP-lijst

- Status: aangenomen
- Datum: 2026-10-23

## Aanleiding
Dev (dev.kleurhoek.nl) is publiek bereikbaar. Vóór de lancering moet een omgeving afgeschermd kunnen worden, zonder Terraform of een nieuwe uitrol.

## Besluit
- **De IP-lijst staat in de database** (`operations.site_access`, één rij per tenant) en wordt beheerd in het admin panel onder *Toegang*. Er zijn twee nieuwe rechten: `operations.access.read` en `operations.access.manage`. Elke wijziging komt in het auditlog.
- **De website-proxy handhaaft.** Hij haalt de stand en de CIDR-blokken elke 30 seconden op via `GET /v1/internal/site-access`, beveiligd met de ingest-sleutel. Hij vergelijkt `cf-connecting-ip` met de lijst (IPv4 en IPv6, via `net.BlockList`). Dat IP-adres is te vertrouwen: verzoeken buiten Cloudflare om worden al geweigerd door de geheime header (ADR 0014). Wie niet op de lijst staat, krijgt een 403 met zijn eigen IP-adres, zodat hij dat kan doorgeven. `/healthz` blijft open.
- **Bij een storing** geldt de laatst bekende lijst. Is er nooit een lijst opgehaald, dan geeft productie een 503; lokaal blijft de site open.
- **Niet buitensluiten.** Aanzetten met een lege lijst kan niet. Aanzetten in het admin panel voegt automatisch het eigen adres van de beheerder toe. Voor IPv6 is dat het /64-blok van de aansluiting, omdat thuisadressen daarbinnen wisselen. Het laatste adres verwijderen terwijl de afscherming aan staat, kan niet.
- **Het admin panel valt er niet onder.** Dat blijft achter Cloudflare Access en Zitadel, zodat je de lijst altijd kunt herstellen.

## Afwegingen
- *Cloudflare Access op de website* was ook mogelijk: sterker en met e-maillogin als je IP wisselt. Maar dan staat de lijst in Terraform en niet in het admin panel. Kan later als extra laag.
- *Gecachete bestanden*: SVG's die Cloudflare al in de cache heeft, kan Cloudflare nog leveren aan iemand buiten de lijst. Pagina's (HTML) cachet Cloudflare niet. Voor een testomgeving is dat aanvaardbaar.

## Aanvulling (2026-10-24): rooktest na een deploy
Met de afscherming aan kreeg de rooktest in GitHub Actions (wisselende IP-adressen) een 403. Daardoor draaide elke deploy naar dev zichzelf terug.

- **Controlesleutel.** Terraform maakt per omgeving een geheime `SITE_CHECK_KEY` (48 tekens). De web-container krijgt hem als geheime variabele, GitHub als environment-secret (via `scripts/infra.sh up`). Een verzoek met de juiste sleutel in `x-kh-check` mag langs de IP-lijst; de proxy vergelijkt in constante tijd en haalt de header weg voordat het verzoek verder gaat. Zonder ingestelde sleutel werkt dit nooit.
- **Gebruikt door** de rooktest en browsertest in Deploy en door de Diagnose-workflow. De sleutel is alleen een uitzondering op de IP-lijst; de geheime header van Cloudflare (ADR 0014) blijft nodig.
- **Terugval** zolang de sleutel nog niet in GitHub staat: krijgt de rooktest de afgeschermd-pagina, dan antwoordt de nieuwe versie wel. De deploy gaat dan door met een waarschuwing en slaat de browsertest over, in plaats van terug te draaien.
