# 0008 · Hosting en uitrol

- Status: aangenomen
- Datum: 2026-10-22

## Besluit
- **Eén Dockerfile met drie targets** (`api`, `web`, `admin`) op Node 22 Alpine, als gebruiker `node`, met `tini` als init. Next.js draait als `standalone`-build. Het token voor GitHub Packages gaat als BuildKit-secret mee en komt niet in de image.
- **Azure Container Apps** in een eigen VNet, één omgeving per stage. De API heeft **geen publieke ingang**: website en admin roepen hem intern aan (mutual TLS binnen de omgeving). SVG's lopen via een route van de website (`/v1/assets/...`), zodat Cloudflare ze kan cachen. Website en admin accepteren alleen verkeer van Cloudflare-IP's.
- **PostgreSQL Flexible Server** alleen via het VNet (geen publiek adres), versie 17. Dev: B1ms. Prod: General Purpose met zone-redundante HA en geo-back-ups.
- **Migraties als Container Apps-job** met dezelfde API-image, gestart door de deploy-workflow vóór de nieuwe versie. Een eenmalige seed-job vult de catalogus.
- **Geheimen** in Key Vault (RBAC), gelezen door een eigen managed identity per app. Geen admin-gebruiker op de registry; apps halen images met hun identity.
- **GitHub Actions met OIDC**: een managed identity met federated credential per omgeving (`environment:dev`, `environment:prod`). Geen Azure-geheimen in GitHub. Prod vraagt goedkeuring via de GitHub-omgeving.
- **Cloudflare**: DNS, Origin CA-certificaat met TLS strict, grove rate limits aan de rand (fijne limieten blijven in de API), Cloudflare Access vóór het admin panel, kaal domein naar www.
- **Zitadel via Terraform**: organisatie, project, apps (JWT-access tokens) en toegang voor Org Beheer. Identity providers en de beheerorganisatie zijn gedeeld en vallen buiten deze repo.
- **Terraform-state** per site in een eigen storage account met Entra-login.

## Afwegingen
- *API intern in plaats van via Cloudflare*: één publieke ingang minder en geen header-vertrouwen van buitenaf. Nadeel: SVG's gaan via de website; Cloudflare cachet ze, dus de extra stap telt alleen bij een cache-miss.
- *Origin CA in plaats van een beheerd certificaat van Azure*: werkt achter de Cloudflare-proxy zonder HTTP-validatie en staat volledig in Terraform.
- *Wachtwoord voor de database*: eenvoudig om mee te beginnen; staat in Key Vault en in de versleutelde state. Volgende stap is Entra-authenticatie met de managed identity van de API.
- *Contributor op de resourcegroep voor de deploy-identity*: genoeg om revisies uit te rollen en jobs te starten. Kan later naar een eigen rol met alleen Container Apps-rechten.

## Regio (22-10-2026)
Sweden Central. West Europe (Amsterdam) neemt op dit moment geen nieuwe klanten aan, en Germany West Central (Frankfurt) biedt een nieuwe subscription geen PostgreSQL Flexible Server aan. Sweden Central heeft alle diensten met beschikbaarheidszones, draait op duurzame energie en is de regio waar Microsoft nieuwe klanten heen stuurt. De extra latency naar Nederland (ca. 25 ms) valt weg achter de cache van Cloudflare. De Terraform-state staat in Frankfurt; dat maakt niet uit.

## Overwogen (22-10-2026)
Europese alternatieven bekeken: Scaleway (goedkoper, Europees, eenvoudiger) en STACKIT (duurder en zwaarder voor deze omvang, geen serverless containers). De eigenaar blijft bij Azure: de infrastructuur staat er al, met managed identities en uitrollen vanuit GitHub zonder sleutels. Omdat de apps gewone containers zijn en de cloud in één Terraform-module zit, blijft overstappen later mogelijk.
