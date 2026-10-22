# Infrastructuur van Kleurhoek

Terraform voor twee omgevingen (`envs/dev`, `envs/prod`), plus `envs/local` dat de Zitadel in `docker compose` inricht (zie de README in de root). Beide gebruiken `modules/site`, dat drie delen samenvoegt:

| Module | Wat |
| --- | --- |
| `modules/zitadel` | Organisatie *Kleurhoek*, het project, de apps *Kleurhoek web* en *Kleurhoek admin* (JWT-access tokens), toegang voor Org Beheer |
| `modules/azure` | Resourcegroep, VNet, PostgreSQL (alleen privé), Container Registry, Key Vault, managed identities, Container Apps (API intern, website en admin alleen via Cloudflare), jobs voor migraties en seed, deploy-identiteit voor GitHub (OIDC) |
| `modules/cloudflare` | DNS, Origin CA-certificaat, TLS strict, rate limits aan de rand, Cloudflare Access voor het admin panel, kaal domein naar www |
| `modules/redirect-domain` | Extra domeinen (`kleurhoek.be`, `kleurhoek.com`) die met pad en query doorsturen naar www.kleurhoek.nl (alleen prod) |

Alles van Kleurhoek staat in eigen accounts en een eigen state, zodat de site los verkocht kan worden.

## Eenmalig vooraf
1. **Azure**: een eigen subscription voor Kleurhoek. Maak de state-opslag aan:
   ```sh
   az group create -n rg-kh-tfstate -l westeurope
   az storage account create -n <uniek, bv. khtfstate123> -g rg-kh-tfstate --sku Standard_ZRS --min-tls-version TLS1_2 --allow-blob-public-access false
   az storage container create -n tfstate --account-name <naam> --auth-mode login
   az role assignment create --role "Storage Blob Data Contributor" --assignee <jouw e-mail> --scope <id van het storage account>
   ```
   Geef bij `terraform init` de naam van het storage account mee: `-backend-config="storage_account_name=<naam>"`.
2. **Cloudflare**: de zones `kleurhoek.nl`, `kleurhoek.be` en `kleurhoek.com` toevoegen (gratis plan; nameservers bij Neostrada aanpassen naar die van Cloudflare). De domeinen staan geregistreerd bij Neostrada. Maak een API-token met alleen de rechten *Zone: DNS Edit, Zone Settings Edit, SSL and Certificates Edit, Zone WAF Edit* voor deze drie zones en *Account: Access: Apps and Policies Edit*. Zet hem als `CLOUDFLARE_API_TOKEN`. In prod vul je de zone-ID's van `.be` en `.com` in bij `redirect_zone_ids`: die sturen door naar www.kleurhoek.nl.
3. **Zitadel Cloud**: instance in de EU-regio. Op het gratis plan is er één instance; dev en prod delen die tot de lancering, elk met een eigen organisatie en eigen apps (Terraform zet "(dev)" achter de namen). Vóór de lancering met echte gebruikers: upgraden naar Pro en prod naar een eigen instance. Instance-instellingen (eenmalig, gedeeld met andere sites):
   - Identity providers Google, Apple en Microsoft toevoegen; noteer hun ID's (`zitadel_idp_ids`).
   - Login-instellingen: login v2, wachtwoorden uit, passkeys en e-mailcode aan.
   - Organisatie *Org Beheer* met verplichte passkeys; noteer het ID (`zitadel_admin_org_id`). Jij bent daar de eerste gebruiker; noteer je gebruikers-ID (`admin_bootstrap_subjects`).
   - Een service user met de rol *IAM Owner* (of *Org Creator* plus *Org Owner* daarna) en een JSON-sleutel voor Terraform. Bewaar die buiten git.
4. Kopieer `envs/<omgeving>/terraform.tfvars.example` naar `terraform.tfvars` en vul in.

## Uitrollen
```sh
cd infra/envs/dev
terraform init -backend-config="storage_account_name=<naam>"
terraform plan -out plan
terraform apply plan
```
De eerste keer draaien de apps een voorbeeldimage. Daarna:

1. Zet in GitHub (repo › Settings › Environments) de omgevingen `dev` en `prod` aan, met voor `prod` een verplichte goedkeuring. Vul per omgeving deze **variables** in (geen geheimen; komen uit `terraform output site`):
   `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (uit `github_deploy`), `ACR_NAME`, `RESOURCE_GROUP`, `SITE_URL`, `MARKETS` (bijv. `nl-nl`).
2. Zet in GitHub (repo › Settings › Secrets and variables › Actions › Variables) de repository-variabele `DEPLOY_ENABLED` op `true`. Tot dan slaat de *Deploy*-workflow pushes naar `main` over. Push daarna naar `main` of start *Deploy* handmatig. De workflow bouwt de images, draait de migraties als job, rolt de drie apps uit en doet een rooktest.
3. Eenmalig per omgeving de catalogus vullen: `az containerapp job start -g <rg> -n caj-kh-<omgeving>-seed`.

## Keuzes
- **API zonder publieke ingang.** Alleen website en admin roepen hem aan, binnen de Container Apps-omgeving (mutual TLS). SVG's lopen via de website en worden door Cloudflare gecachet.
- **Alleen Cloudflare mag de origin bereiken**: de ingang van website en admin accepteert alleen de IP-ranges van Cloudflare, met een Origin CA-certificaat en TLS strict.
- **Geheimen in Key Vault**, gelezen door de managed identity van elke app. Terraform maakt ze aan (sessiesleutels, ingest-sleutel, databasewachtwoord, OIDC-client-secrets); ze staan dus ook in de state, die daarom alleen met Entra-login te lezen is.
- **Database**: de API verbindt nu met de beheerdersrol en schakelt per transactie naar `app_user` (row-level security). Volgende stap: inloggen met de managed identity (Entra) in plaats van een wachtwoord.
- **Productie bouwt opnieuw** vanaf dezelfde commit (lockfile vast). Later: images uit dev promoveren in plaats van opnieuw bouwen.
