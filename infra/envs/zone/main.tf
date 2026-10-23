# De zone kleurhoek.nl in Cloudflare (gedeeld door dev en prod) plus de doorstuur-domeinen
# kleurhoek.be en kleurhoek.com. Eén keer toepassen vóór de omgevingen. Draaien: zie infra/README.md.

terraform {
  required_version = ">= 1.10"
  required_providers {
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    random     = { source = "hashicorp/random", version = "~> 3.7" }
  }
  # State in een privé bucket in Scaleway Object Storage (eigen account per site: verkoopbaar).
  # Bucket: `-backend-config="bucket=<naam>"`. Sleutel: AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY = je Scaleway-API-sleutel.
  backend "s3" {
    key                         = "kleurhoek-zone.tfstate"
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

# API-token in CLOUDFLARE_API_TOKEN; rechten: zie infra/README.md.
provider "cloudflare" {}

variable "cloudflare_zone_id" {
  type        = string
  description = "Zone-ID van kleurhoek.nl."
}
variable "prod_live" {
  type        = bool
  default     = false
  description = "Zodra www.kleurhoek.nl draait: kaal domein en .be/.com sturen door naar www."
}
variable "redirect_zone_ids" {
  type        = map(string)
  default     = {}
  description = "Extra domeinen die doorsturen naar www.kleurhoek.nl, met hun zone-ID. Bijvoorbeeld { \"kleurhoek.be\" = \"...\", \"kleurhoek.com\" = \"...\" }."
}
variable "zitadel_login_cname" {
  type    = string
  default = null
}
variable "edge_rate_limits" {
  type = list(object({ name = string, expression = string, requests = number, period = number, block_for = number }))
  # Gratis plan: één regel, period 10 seconden. Op Pro: aparte regels per minuut (zie infra/README.md).
  default = [{
    name       = "inloggen-en-analytics"
    expression = "(starts_with(http.request.uri.path, \"/auth/\") or http.request.uri.path eq \"/e\")"
    requests   = 30
    period     = 10
    block_for  = 10
  }]
}

# Het account van de zone (voor de Worker); zo hoeft het account-ID niet in de tfvars.
data "cloudflare_zone" "main" {
  zone_id = var.cloudflare_zone_id
}

module "zone" {
  source     = "../../modules/cloudflare-zone"
  zone_id    = var.cloudflare_zone_id
  account_id = data.cloudflare_zone.main.account.id
  domain     = "kleurhoek.nl"
  environments = {
    dev  = { site = "dev", admin = "admin-dev", login = "login-dev" }
    prod = { site = "www", admin = "admin", login = "login" }
  }
  apex_redirect    = var.prod_live
  login_cname      = var.zitadel_login_cname
  edge_rate_limits = var.edge_rate_limits
}

# kleurhoek.be en kleurhoek.com sturen door naar de Nederlandse site (pad blijft behouden).
# Gaat een markt live met een eigen domein, dan krijgt dat domein een eigen site-configuratie (ADR 0013).
module "redirect_domain" {
  source   = "../../modules/redirect-domain"
  for_each = var.prod_live ? var.redirect_zone_ids : {}
  zone_id  = each.value
  domain   = each.key
  target   = "https://www.kleurhoek.nl"
}

output "worker_secrets" {
  value     = module.zone.worker_secrets
  sensitive = true
}

output "edge_secrets" {
  value     = module.zone.edge_secrets
  sensitive = true
}
