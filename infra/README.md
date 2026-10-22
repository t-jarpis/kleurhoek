# Infrastructuur van Kleurhoek

Kleurhoek draait bij **Scaleway in Amsterdam** (`nl-ams`), achter **Cloudflare**, met inloggen via **Zitadel Cloud** (ADR 0014). Terraform heeft drie configuraties, plus `envs/local` dat de Zitadel in `docker compose` inricht (zie de README in de root):

| Configuratie | Wat |
| --- | --- |
| `envs/zone` | De zone kleurhoek.nl, gedeeld door dev en prod: TLS strict, CAA, redirects, cacheregel, rate limits en de geheime header per omgeving. Na de lancering ook `kleurhoek.be` en `kleurhoek.com` als doorstuur-domeinen. Eén keer vóór de omgevingen. |
| `envs/dev`, `envs/prod` | Eén omgeving via `modules/site`. |

`modules/site` bestaat uit drie modules:

| Module | Wat |
| --- | --- |
| `modules/zitadel` | Organisatie, project, apps *Kleurhoek web* en *Kleurhoek admin*, toegang voor Org Beheer. |
| `modules/scaleway` | VPC met privénetwerk, PostgreSQL (alleen privé), Container Registry, Serverless Containers (API alleen privé, website en admin via Cloudflare) en de IAM-applicatie waarmee GitHub uitrolt. |
| `modules/cloudflare` | DNS-records naar de containers en Cloudflare Access voor het admin panel. |

Alles van Kleurhoek staat in eigen accounts (Scaleway-organisatie *Kleurhoek*, Cloudflare-zone, Zitadel-organisatie) en een eigen state, zodat de site los verkocht kan worden.

## Eenmalig vooraf
1. **Scaleway**: organisatie *Kleurhoek* met de projecten `kleurhoek-dev` en (later) `kleurhoek-prod`.
   - Maak onder *IAM › API keys* een API-sleutel voor jezelf. Kies als *preferred project* `kleurhoek-dev`, en bij *Object Storage* ook `kleurhoek-dev`.
   - Maak in `kleurhoek-dev` een bucket voor de state. Regio Amsterdam, privé, met versioning aan; de naam moet wereldwijd uniek zijn, bijvoorbeeld `kleurhoek-tfstate-<iets>`. De state van zone, dev en prod komt in deze ene bucket, elk met een eigen sleutel.
   - Zet de sleutel in je shell. Bewaar hem in `~/.config/kleurhoek/scaleway.env`, niet in git en niet in iCloud:
     ```sh
     export SCW_ACCESS_KEY=… SCW_SECRET_KEY=…
     export AWS_ACCESS_KEY_ID=$SCW_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$SCW_SECRET_KEY   # voor de state-bucket
     export CLOUDFLARE_API_TOKEN=…
     ```
2. **Cloudflare**: de zones `kleurhoek.nl`, `kleurhoek.be` en `kleurhoek.com` (gratis plan; nameservers bij Neostrada). API-token met *Zone: DNS Edit, Zone Settings Edit, SSL and Certificates Edit, Zone WAF Edit, Cache Rules Edit, Transform Rules Edit, Dynamic Redirect Edit* voor deze zones en *Account: Access: Apps and Policies Edit*.
3. **Zitadel Cloud**: instance in de EU-regio. Op het gratis plan is er één instance; dev en prod delen die tot de lancering, elk met een eigen organisatie en apps.
   - Identity providers Google, Apple en Microsoft (ID's in `zitadel_idp_ids`).
   - Login v2, wachtwoorden uit, passkeys en e-mailcode aan.
   - Organisatie *Org Beheer* met verplichte passkeys (`zitadel_admin_org_id`). Je eigen gebruikers-ID gaat in `admin_bootstrap_subjects`.
   - Een service user met *IAM Owner* en een JSON-sleutel in `~/.config/kleurhoek/`.
4. Kopieer per configuratie `terraform.tfvars.example` naar `terraform.tfvars` en vul in. De organisatie-ID staat in de Scaleway-console onder *Organization › Settings*, de project-ID onder *Project › Settings*.

## Eerste uitrol (dev)
Containers kunnen pas bestaan als er images zijn, en images komen uit GitHub. Daarom gaat de eerste keer in twee stappen.

```sh
# 1. De zone (één keer; daarna alleen bij wijzigingen)
cd infra/envs/zone
terraform init -backend-config="bucket=<state-bucket>"
terraform apply

# 2. Dev zonder containers: netwerk, database, registry, Zitadel, Access, deploy-sleutel
cd ../dev
terraform init -backend-config="bucket=<state-bucket>"
terraform apply -var apps_enabled=false
```

3. **GitHub-omgeving `dev`** vullen vanuit de output. De sleutel gaat niet via je scherm.
   ```sh
   out=$(terraform output -json github)
   for k in SCW_ACCESS_KEY SCW_PROJECT_ID SCW_REGION REGISTRY CONTAINER_IDS SITE_URL MARKETS; do
     gh variable set "$k" -e dev -R t-jarpis/kleurhoek -b "$(jq -r ".variables.$k" <<<"$out")"
   done
   jq -r .secrets.SCW_SECRET_KEY <<<"$out" | gh secret set SCW_SECRET_KEY -e dev -R t-jarpis/kleurhoek
   gh variable set DEPLOY_ENABLED -R t-jarpis/kleurhoek -b true
   ```
4. **Images bouwen**: `gh workflow run Deploy -R t-jarpis/kleurhoek -f environment=dev`. Zonder containers stopt de workflow na het pushen.
5. **Containers en domeinen**: `terraform apply`. Daarna `CONTAINER_IDS` opnieuw zetten (de regel uit stap 3 voor die ene variabele). Vanaf nu rolt elke push naar `main` automatisch uit naar dev.

De eerste start van de API maakt de tabellen aan en vult de catalogus. Het eigen domein krijgt binnen enkele minuten een certificaat; tot dan geeft Cloudflare een 526.

## Daarna
- **Uitrollen**: push naar `main` (dev), of start *Deploy* met `environment=prod` (vraagt goedkeuring). De workflow bouwt, pusht, zet de image per container (eerst de API, die migreert) en doet een rooktest.
- **Infra wijzigen**: `terraform plan` en `terraform apply` in de betreffende map. Terraform kijkt niet naar de image van de containers; die beheert GitHub.
- **Deploy-sleutel roteren**: `terraform apply -replace=module.site.module.scaleway.scaleway_iam_api_key.deploy`, daarna het secret opnieuw zetten (stap 3).

## Productie
Pas bij de lancering: project `kleurhoek-prod`, `envs/prod/terraform.tfvars`, dezelfde stappen 2 tot en met 5 met omgeving `prod` (in GitHub met verplichte goedkeuring). Daarna in `envs/zone`: `prod_live = true` en `apply`. Dan sturen het kale domein, `kleurhoek.be` en `kleurhoek.com` door naar www.

Controleer vooraf de database-node: `scw rdb node-type list region=nl-ams`.

## Keuzes
- **API zonder publieke ingang.** Alleen website en admin roepen hem aan, via het privénetwerk. SVG's lopen via de website en worden door Cloudflare gecachet.
- **Alleen via Cloudflare.** Cloudflare zet een geheime header per omgeving; website en admin weigeren verzoeken zonder (behalve `/healthz`). Daarmee kan niemand via de standaard-hostnaam van Scaleway om de WAF, de rate limits of Access heen.
- **Certificaten** van Let's Encrypt via Scaleway (HTTP-01). Daarom staat *Always Use HTTPS* uit en doet een eigen regel de redirect, met een uitzondering voor `/.well-known/acme-challenge/`.
- **Database alleen privé**, met TLS tegen de CA van de instance. De API verbindt met de beheerdersrol en schakelt per transactie naar `app_user` (row-level security).
- **Migraties bij het opstarten van de API**, achter een advisory lock. Serverless Jobs kunnen niet aan een privénetwerk.
- **Productie bouwt opnieuw** vanaf dezelfde commit (lockfile vast). Later: images uit dev promoveren.
