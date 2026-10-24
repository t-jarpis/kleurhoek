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
2. **Cloudflare**: de zones `kleurhoek.nl`, `kleurhoek.be` en `kleurhoek.com` (gratis plan; nameservers bij Neostrada). API-token met *Zone: DNS Edit, Zone Settings Edit, SSL and Certificates Edit, Zone WAF Edit, Cache Rules Edit, Transform Rules Edit, Single Redirect Edit, Workers Routes Edit* voor deze zones en *Account: Access: Apps and Policies Edit, Workers Scripts Edit*. `scripts/infra.sh check` controleert dit.
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

## Organisaties en hun domeinen (ADR 0017)
- **Subdomein: niets te doen.** Een organisatie die in het admin panel wordt aangemaakt, is meteen bereikbaar op `{code}.kleurhoek.nl` (prod) of `{code}-dev.kleurhoek.nl` (dev). Eén wildcard-record `*.kleurhoek.nl` wijst naar de Worker `kleurhoek-organisaties` (`modules/cloudflare-zone/org-worker.js`). Die stuurt door naar de website van de omgeving met de oorspronkelijke host, het IP-adres en het land, plus een eigen geheim (`ORG_WORKER_SECRET`). Zonder dat geheim negeert de website die headers. De vaste hosts (www, dev, admin, login …) slaan de Worker over. Universal SSL dekt `*.kleurhoek.nl`.
- **Eigen domein van een school** (bijvoorbeeld `kleuren.deregenboog.nl`): vul het in bij de organisatie (Algemeen › Eigen domeinen). Een CNAME van een ander Cloudflare-account naar ons wordt door Cloudflare geweigerd (fout 1014), dus dit vraagt *Cloudflare for SaaS* (custom hostnames; de eerste 100 zijn gratis) met de Worker als fallback-origin. Dat staat nog niet in Terraform; tot dan is het subdomein de weg.

## Problemen zoeken
Workflow **Diagnose** (Actions › Diagnose › Run workflow, of `gh workflow run Diagnose -R t-jarpis/kleurhoek -f environment=dev`):
- standaard: status en foutmelding van de drie containers, en de HTTP-status van de website;
- met `deep`: draait de API even met `.github/diagnose/api-startup.js` (zelfde image en geheimen), dat de database controleert en migraties en seed uitvoert met de echte PostgreSQL-fout. Daarna wordt alles teruggezet.

Zo zijn fouten te vinden zonder de Scaleway-console.

## Productie
`scripts/infra.sh up prod` doet alles, en vraagt bij elke Terraform-wijziging om bevestiging:
1. Het Scaleway-project `kleurhoek-prod` zoeken of aanmaken en het ID in `envs/prod/terraform.tfvars` zetten. De rest van dat bestand is gelijk aan dev.
2. Zone, dan de omgeving (eerst de basis, dan de images via *Deploy*, dan de containers), GitHub-omgeving `prod` met jouw goedkeuring (als het GitHub-plan dat toestaat).
3. Rooktest op www.kleurhoek.nl, daarna live: `prod_live = true` en de zone-ID's van `kleurhoek.be` en `kleurhoek.com` in `envs/zone/terraform.tfvars`, en de zone opnieuw toepassen. Het kale domein en de extra domeinen sturen dan door naar www.

De database begint klein (DB-PLAY2-PICO, één node, back-up 35 dagen in een ander datacenter, ADR 0021). De catalogus komt bij elke start van de API uit `@kleurhoek/catalog-data` (aanvullend). Producten, partners en organisaties zet je in het admin panel van productie; dev en prod delen geen data.

Controleer vooraf de database-node: `scw rdb node-type list region=nl-ams`.

## Keuzes
- **API zonder publieke ingang.** Alleen website en admin roepen hem aan, via het privénetwerk. SVG's lopen via de website en worden door Cloudflare gecachet.
- **Alleen via Cloudflare.** Cloudflare zet een geheime header per omgeving; website en admin weigeren verzoeken zonder (behalve `/healthz`). Daarmee kan niemand via de standaard-hostnaam van Scaleway om de WAF, de rate limits of Access heen.
- **Certificaten** van Let's Encrypt via Scaleway (HTTP-01). Daarom staat *Always Use HTTPS* uit en doet een eigen regel de redirect, met een uitzondering voor `/.well-known/acme-challenge/`.
- **Database alleen privé**, met TLS tegen de CA van de instance. De API verbindt met de beheerdersrol en schakelt per transactie naar `app_user` (row-level security).
- **Migraties bij het opstarten van de API**, achter een advisory lock. Serverless Jobs kunnen niet aan een privénetwerk.
- **Productie bouwt opnieuw** vanaf dezelfde commit (lockfile vast). Later: images uit dev promoveren.
