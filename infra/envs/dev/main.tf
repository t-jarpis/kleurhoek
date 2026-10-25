# Omgeving: dev. Draaien: zie infra/README.md.

terraform {
  required_version = ">= 1.10"
  required_providers {
    scaleway   = { source = "scaleway/scaleway", version = "~> 2.88" }
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    zitadel    = { source = "zitadel/zitadel", version = "~> 3.8" }
    random     = { source = "hashicorp/random", version = "~> 3.7" }
  }
  # State in een privé bucket in Scaleway Object Storage (eigen account per site: verkoopbaar).
  # Bucket: `-backend-config="bucket=<naam>"`. Sleutel: AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY = je Scaleway-API-sleutel.
  backend "s3" {
    key                         = "kleurhoek-dev.tfstate"
    region                      = "nl-ams"
    endpoints                   = { s3 = "https://s3.nl-ams.scw.cloud" }
    use_path_style              = true
    use_lockfile                = true
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }
}

# Sleutel via SCW_ACCESS_KEY en SCW_SECRET_KEY (zie infra/README.md).
provider "scaleway" {
  region          = "nl-ams"
  zone            = "nl-ams-1"
  organization_id = var.scaleway_organization_id
  project_id      = var.scaleway_project_id
}

# API-token in CLOUDFLARE_API_TOKEN; rechten: zie infra/README.md.
provider "cloudflare" {}

# Service user in Zitadel met de rol Org Owner op de Kleurhoek-organisatie en Org Beheer (project grant).
provider "zitadel" {
  domain           = var.zitadel_domain
  insecure         = false
  port             = "443"
  jwt_profile_file = var.zitadel_key_file
}

variable "scaleway_organization_id" { type = string }
variable "scaleway_project_id" {
  type        = string
  description = "ID van het project kleurhoek-dev."
}
variable "state_bucket" {
  type        = string
  description = "Dezelfde bucket als bij terraform init; hieruit komt de state van envs/zone."
}
variable "apps_enabled" {
  type        = bool
  default     = true
  description = "Alleen bij de allereerste apply op false: dan bestaan de images nog niet."
}
variable "zitadel_domain" { type = string }
variable "zitadel_key_file" {
  type        = string
  description = "Pad naar de JSON-sleutel van de Zitadel service user (niet in git)."
}
variable "cloudflare_account_id" { type = string }
variable "cloudflare_zone_id" { type = string }
variable "zitadel_admin_org_id" { type = string }
variable "zitadel_idp_ids" {
  type    = list(string)
  default = []
}
variable "admin_emails" { type = list(string) }
variable "mail" {
  type = object({
    from                   = string
    smtp_url               = optional(string, "")
    transactional_smtp_url = optional(string, "")
  })
  sensitive = true
  default   = { from = "Kleurhoek <hallo@kleurhoek.nl>" }
}
variable "search" {
  type = object({
    google_key_file = optional(string, "")
    bing_api_key    = optional(string, "")
  })
  sensitive   = true
  default     = {}
  description = "Zoekcijfers (ADR 0041): pad naar de JSON-sleutel van het Google-serviceaccount (niet in git) en de Bing-API-sleutel. Alleen prod gebruikt ze."
}
variable "admin_bootstrap_subjects" {
  type    = list(string)
  default = []
}

# Instellingen voor de hele zone (en de geheime header van deze omgeving) komen uit envs/zone.
data "terraform_remote_state" "zone" {
  backend = "s3"
  config = {
    bucket                      = var.state_bucket
    key                         = "kleurhoek-zone.tfstate"
    region                      = "nl-ams"
    endpoints                   = { s3 = "https://s3.nl-ams.scw.cloud" }
    use_path_style              = true
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }
}

module "site" {
  source                   = "../../modules/site"
  environment              = "dev"
  domain                   = "kleurhoek.nl"
  subdomains               = { site = "dev", admin = "admin-dev", login = "login-dev" }
  cloudflare_account_id    = var.cloudflare_account_id
  cloudflare_zone_id       = var.cloudflare_zone_id
  zitadel_issuer           = "https://${var.zitadel_domain}"
  zitadel_admin_org_id     = var.zitadel_admin_org_id
  zitadel_idp_ids          = var.zitadel_idp_ids
  admin_emails             = var.admin_emails
  admin_bootstrap_subjects = var.admin_bootstrap_subjects
  edge_secret              = data.terraform_remote_state.zone.outputs.edge_secrets["dev"]
  org_worker_secret        = data.terraform_remote_state.zone.outputs.worker_secrets["dev"]
  org_host_pattern         = "{slug}-dev.kleurhoek.nl"
  apps_enabled             = var.apps_enabled
  mail                     = var.mail
  # Domeinen per land (ADR 0040), zodra ze in envs/zone bestaan.
  market_domains = try(data.terraform_remote_state.zone.outputs.market_domains["dev"], [])
  search         = var.search
  # Goedkoopste node (circa € 11 per maand), geen HA, back-up dagelijks (7 dagen) in een ander datacenter.
  # Niet beschikbaar in nl-ams? Dan DB-PLAY2-PICO (circa € 17). Controleer: scw rdb node-type list region=nl-ams.
  database = {
    node_type      = "DB-DEV-S"
    engine         = "PostgreSQL-16"
    volume_gb      = 5
    ha             = false
    backup_days    = 7
    backup_hours   = 24
    backup_same_dc = false
  }
  # Dev mag naar nul schalen: kost niets als niemand kijkt (eerste verzoek duurt dan enkele seconden).
  scale = { api_min = 0, api_max = 2, web_min = 0, web_max = 2 }
}

output "site_url" { value = module.site.site_url }
output "admin_url" { value = module.site.admin_url }
output "registry_endpoint" { value = module.site.registry_endpoint }
output "container_ids" { value = module.site.container_ids }
output "github" {
  value     = module.site.github
  sensitive = true
}
