# Omgeving: prod. Draaien: zie infra/README.md.

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
    key                         = "kleurhoek-prod.tfstate"
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
  description = "ID van het project kleurhoek-prod."
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
variable "social" {
  type = object({
    pinterest_app_id     = optional(string, "")
    pinterest_app_secret = optional(string, "")
    meta_app_id          = optional(string, "")
    meta_app_secret      = optional(string, "")
  })
  sensitive   = true
  default     = {}
  description = "Social (ADR 0063): app-ID's en -geheimen van Pinterest en Meta (Facebook en Instagram). Leeg = dat kanaal is niet te koppelen."
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
  environment              = "prod"
  domain                   = "kleurhoek.nl"
  subdomains               = { site = "www", admin = "admin", login = "login" }
  cloudflare_account_id    = var.cloudflare_account_id
  cloudflare_zone_id       = var.cloudflare_zone_id
  zitadel_issuer           = "https://${var.zitadel_domain}"
  zitadel_admin_org_id     = var.zitadel_admin_org_id
  zitadel_idp_ids          = var.zitadel_idp_ids
  admin_emails             = var.admin_emails
  admin_bootstrap_subjects = var.admin_bootstrap_subjects
  edge_secret              = data.terraform_remote_state.zone.outputs.edge_secrets["prod"]
  org_worker_secret        = data.terraform_remote_state.zone.outputs.worker_secrets["prod"]
  org_host_pattern         = "{slug}.kleurhoek.nl"
  apps_enabled             = var.apps_enabled
  mail                     = var.mail
  # Domeinen per land (ADR 0040), zodra ze in envs/zone bestaan.
  market_domains = try(data.terraform_remote_state.zone.outputs.market_domains["prod"], [])
  search         = var.search
  social         = var.social
  # Klein starten (circa € 20 per maand): één node, dagelijkse back-up 35 dagen in een ander datacenter.
  # Groeien = node_type ophogen (bijv. DB-PLAY2-NANO of DB-PRO2-XXS) en eventueel ha = true; kort onderbreking.
  database = {
    node_type      = "DB-PLAY2-PICO"
    engine         = "PostgreSQL-16"
    volume_gb      = 10
    ha             = false
    backup_days    = 35
    backup_hours   = 24
    backup_same_dc = false
  }
  # Altijd één API en één website warm (ADR 0043): geen wachttijd voor de eerste bezoeker na een stille
  # periode (circa € 30 per maand extra). Admin en inlogpagina mogen wel naar nul.
  scale = { api_min = 1, api_max = 6, web_min = 1, web_max = 10 }
}

output "site_url" { value = module.site.site_url }
output "admin_url" { value = module.site.admin_url }
output "registry_endpoint" { value = module.site.registry_endpoint }
output "container_ids" { value = module.site.container_ids }
output "github" {
  value     = module.site.github
  sensitive = true
}
