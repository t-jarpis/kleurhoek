# 0014 · Hosting bij Scaleway

- Status: aangenomen
- Datum: 2026-10-23
- Vervangt: [0008](0008-hosting-en-uitrol.md) (het Azure-deel)

## Aanleiding
Azure kon Kleurhoek niet hosten: West Europe neemt geen nieuwe klanten aan, Germany West Central biedt nieuwe subscriptions geen PostgreSQL, en Sweden Central gaf herhaaldelijk capaciteitsfouten. Scaleway was al het Europese alternatief uit 0008 (goedkoper, eenvoudiger, Nederlands datacenter).

## Besluit
- **Regio Amsterdam (`nl-ams`)**, een eigen Scaleway-organisatie *Kleurhoek* met een project per omgeving (`kleurhoek-dev`, `kleurhoek-prod`). Verkoopbaar: de organisatie gaat in zijn geheel over.
- **Serverless Containers** voor `api`, `web` en `admin`, in één namespace per omgeving en allemaal aan een **privénetwerk** (VPC).
  - De API heeft **alleen een privé-endpoint**, geen publieke ingang. Website en admin roepen hem daarover aan.
  - Website en admin hebben een eigen domein (`scaleway_container_domain`, certificaat van Let's Encrypt) achter de Cloudflare-proxy.
  - Dev schaalt naar nul, prod houdt minstens één instance warm.
- **Alleen via Cloudflare.** Het gratis plan van Cloudflare kan geen Host-header naar de origin herschrijven en Scaleway kent geen IP-filter op containers.
  - Daarom zet Cloudflare een geheime header (`x-kleurhoek-edge`, per omgeving) op elk verzoek, en weigeren website en admin verzoeken zonder (behalve `/healthz`).
  - Zo komt niemand via de standaard-hostnaam van Scaleway langs de WAF, de rate limits of Cloudflare Access heen.
- **TLS strict** met het Let's Encrypt-certificaat van Scaleway. De HTTP-01-controle moet ongecachet tot aan de container kunnen. Daarom:
  - staat *Always Use HTTPS* uit en stuurt een eigen redirect-regel alles behalve `/.well-known/acme-challenge/` naar HTTPS;
  - is er een cacheregel die dat pad overslaat;
  - staat er een CAA-record voor letsencrypt.org.
- **Managed PostgreSQL 16** zonder publiek endpoint (alleen het privénetwerk), versleuteld at rest. TLS met controle tegen de CA van de instance (`DATABASE_CA`).
  - Dev: `DB-PLAY2-PICO`, de goedkoopste, zonder HA.
  - Prod: HA, met back-ups in een ander datacenter.
- **Migraties bij het opstarten van de API** (`MIGRATE_ON_START`), achter een advisory lock, zodat parallelle instances na elkaar migreren. Serverless Jobs kunnen niet aan een privénetwerk, dus een aparte migratiejob kan de database niet bereiken. In dev vult de API ook de catalogus (`SEED_ON_START`, idempotent).
- **Geheimen** als *secret environment variables* van de containers (versleuteld opgeslagen). Terraform maakt ze aan; ze staan dus ook in de state.
- **Container Registry** per omgeving (privé). GitHub bouwt en pusht `:<commit>` en `:latest`, en zet daarna de image van elke container via de Containers-API: eerst de API (die migreert), dan website en admin. Een rooktest volgt.
- **Uitrollen vanuit GitHub met een eigen IAM-applicatie per omgeving.** Die mag alleen Container Registry en Containers beheren, binnen het project van die omgeving. De API-sleutel staat als geheim in de GitHub-omgeving. Scaleway kent geen OIDC-federatie met GitHub.
- **Terraform-state** in een privé bucket in Scaleway Object Storage (S3-backend met `use_lockfile`).
- **Zone-instellingen apart** (`infra/envs/zone`). Cloudflare kent per zone één ruleset per fase, dus dev en prod kunnen die niet elk beheren zonder elkaar te overschrijven. De omgevingen beheren alleen hun eigen DNS-records en Access-applicatie. De geheime header per omgeving komt uit de zone-state.

## Afwegingen
- *Geheime header in plaats van IP-filter*: minder sterk dan een netwerkfilter, maar de waarde is lang en willekeurig, wordt alleen door Cloudflare gezet en overschrijft wat een bezoeker zelf meestuurt. Met Cloudflare Enterprise (of een Worker) kan het later via mTLS of een eigen origin.
- *Migreren bij het opstarten*: geen aparte stap meer in de pijplijn. Een mislukte migratie houdt de nieuwe API tegen (de startup probe faalt) terwijl de oude versie blijft draaien. Migraties blijven daarom achterwaarts compatibel (expand/contract).
- *API-sleutel in GitHub in plaats van OIDC*: kleinst mogelijke rechten, per omgeving en te roteren met `terraform apply -replace`.
- *Koude start in dev*: na 15 minuten zonder verkeer schaalt dev naar nul; het eerste verzoek duurt dan enkele seconden.

## Kosten (indicatie per maand)
- **Dev**: database `DB-PLAY2-PICO` rond € 10. Containers vallen bij weinig verkeer grotendeels in het gratis tegoed (200.000 vCPU-s en 400.000 GB-s per maand). Registry en state samen enkele euro's.
- **Prod**: een HA-database en altijd één warme instance van API en website, in de orde van € 80–150. Dat hangt af van de database-node en het verkeer.
