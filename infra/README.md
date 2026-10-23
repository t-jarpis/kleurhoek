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
2. **Cloudflare**: de zones `kleurhoek.nl`, `kleurhoek.be` en `kleurhoek.com` (gratis plan; nameservers bij Neostrada). API-token met *Zone: DNS Edit, Zone Settings Edit, SSL and Certificates Edit, Zone WAF Edit, Cache Rules Edit, Transform Rules Edit, Single Redirect Edit* voor deze zones en *Account: Access: Apps and Policies Edit*.
3. **Zitadel Cloud**: instance in de EU-regio. Op het gratis plan is er één instance; dev en prod delen die tot de lancering, elk met een eigen organisatie en apps.
   - Identity providers Google, Apple en Microsoft (ID's in `zitadel_idp_ids`).
   - Login v2, wachtwoorden uit, passkeys en e-mailcode aan.
   - Organisatie *Org Beheer* met verplichte passkeys (`zitadel_admin_org_id`). Je eigen gebruikers-ID gaat in `admin_bootstrap_subjects`.
   - Een service user met *IAM Owner* en een JSON-sleutel in `~/.config/kleurhoek/`.
4. Kopieer per configuratie `terraform.tfvars.example` naar `terraform.tfvars` en vul in. De organisatie-ID staat in de Scaleway-console onder *Organization › Settings*, de project-ID onder *Project › Settings*.

## Uitrollen: één commando
```sh
scripts/infra.sh check      # alleen controleren; meldt alles wat ontbreekt in één lijst
scripts/infra.sh up dev     # alles: zone, omgeving, GitHub, eerste images, containers, rooktest
```
Het script:
- installeert of werkt bij wat ontbreekt (terraform, gh, jq via Homebrew);
- vraagt de Scaleway-sleutel en het Cloudflare-token één keer en bewaart ze in de macOS-sleutelhanger (dienst `kleurhoek`); `scripts/infra.sh reset-keys` vergeet ze weer;
- controleert sleutels, project, zone, tfvars, Zitadel-sleutel en GitHub-login live, vóór er iets verandert;
- maakt de state-bucket aan als die er niet is (versioning aan);
- past Terraform toe zonder vragen zolang er niets verwijderd wordt, en stopt met uitleg bij een 403 (ontbrekend recht op het token);
- vult de GitHub-omgeving, laat de eerste images bouwen en maakt daarna de containers aan;
- wacht tot de site antwoordt.

Opnieuw draaien is altijd veilig: het gaat verder waar het bleef. Wat je zelf moet doen (accounts, een API-sleutel en token aanmaken, `gh auth login`) staat hierboven onder *Eenmalig vooraf*; het script zegt precies wat er nog ontbreekt.

De eerste start van de API maakt de tabellen aan en vult de catalogus. Het eigen domein krijgt binnen enkele minuten een certificaat; tot dan geeft Cloudflare een 526.

## Daarna
- **Uitrollen**: push naar `main` (dev), of start *Deploy* met `environment=prod` (vraagt goedkeuring). De workflow bouwt, pusht, zet de image per container (eerst de API, die migreert) en doet een rooktest.
- **Infra wijzigen**: `scripts/infra.sh up dev` (of `prod`). Terraform kijkt niet naar de image van de containers; die beheert GitHub.
- **Deploy-sleutel roteren**: `terraform apply -replace=module.site.module.scaleway.scaleway_iam_api_key.deploy`, daarna `scripts/infra.sh up dev`; dat zet het nieuwe secret in GitHub.

## Productie
Pas bij de lancering: project `kleurhoek-prod`, `envs/prod/terraform.tfvars` invullen en `scripts/infra.sh up prod` (vraagt bij elke wijziging om bevestiging). Zet in GitHub voor de omgeving `prod` een verplichte goedkeuring. Daarna in `envs/zone`: `prod_live = true` en `apply`. Dan sturen het kale domein, `kleurhoek.be` en `kleurhoek.com` door naar www.

Controleer vooraf de database-node: `scw rdb node-type list region=nl-ams`.

## Keuzes
- **API zonder publieke ingang.** Alleen website en admin roepen hem aan, via het privénetwerk. SVG's lopen via de website en worden door Cloudflare gecachet.
- **Alleen via Cloudflare.** Cloudflare zet een geheime header per omgeving; website en admin weigeren verzoeken zonder (behalve `/healthz`). Daarmee kan niemand via de standaard-hostnaam van Scaleway om de WAF, de rate limits of Access heen.
- **Certificaten** van Let's Encrypt via Scaleway (HTTP-01). Daarom staat *Always Use HTTPS* uit en doet een eigen regel de redirect, met een uitzondering voor `/.well-known/acme-challenge/`.
- **Database alleen privé**, met TLS tegen de CA van de instance. De API verbindt met de beheerdersrol en schakelt per transactie naar `app_user` (row-level security).
- **Migraties bij het opstarten van de API**, achter een advisory lock. Serverless Jobs kunnen niet aan een privénetwerk.
- **Productie bouwt opnieuw** vanaf dezelfde commit (lockfile vast). Later: images uit dev promoveren.
