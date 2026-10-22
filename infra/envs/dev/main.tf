# Omgeving: dev. Draaien: zie infra/README.md.

terraform {
  required_version = ">= 1.10"
  required_providers {
    azurerm    = { source = "hashicorp/azurerm", version = "~> 5.10" }
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    zitadel    = { source = "zitadel/zitadel", version = "~> 3.8" }
    random     = { source = "hashicorp/random", version = "~> 3.7" }
    tls        = { source = "hashicorp/tls", version = "~> 4.1" }
  }
  # State in een eigen storage account per site (verkoopbaar), met Entra-login in plaats van sleutels.
  backend "azurerm" {
    resource_group_name = "rg-kh-tfstate"
    container_name      = "tfstate"
    key                 = "kleurhoek-dev.tfstate"
    use_azuread_auth    = true
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
  subscription_id = var.azure_subscription_id
}

# API-token met alleen: Zone DNS, Zone Settings, SSL and Certificates, Zone WAF (rulesets) en Access.
provider "cloudflare" {}

# Service user in Zitadel met de rol Org Owner op de Kleurhoek-organisatie en Org Beheer (project grant).
provider "zitadel" {
  domain           = var.zitadel_domain
  insecure         = false
  port             = "443"
  jwt_profile_file = var.zitadel_key_file
}

variable "azure_subscription_id" { type = string }
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
variable "admin_bootstrap_subjects" {
  type    = list(string)
  default = []
}

module "site" {
  source                   = "../../modules/site"
  environment              = "dev"
  domain                   = "kleurhoek.nl"
  subdomains               = { site = "dev", admin = "admin-dev" }
  cloudflare_account_id    = var.cloudflare_account_id
  cloudflare_zone_id       = var.cloudflare_zone_id
  zitadel_issuer           = "https://${var.zitadel_domain}"
  zitadel_admin_org_id     = var.zitadel_admin_org_id
  zitadel_idp_ids          = var.zitadel_idp_ids
  admin_emails             = var.admin_emails
  admin_bootstrap_subjects = var.admin_bootstrap_subjects
  postgres = {
    sku_name          = "B_Standard_B1ms"
    storage_mb        = 32768
    high_availability = false
    backup_days       = 7
  }
  # Dev mag naar nul schalen: kost niets als niemand kijkt (eerste verzoek duurt dan een paar seconden).
  replicas = { api_min = 0, api_max = 2, web_min = 0, web_max = 2 }
  # Gratis plan: één regel, period 10 seconden.
  edge_rate_limits = [{
    name       = "inloggen-en-api"
    expression = "(starts_with(http.request.uri.path, \"/auth/\") or starts_with(http.request.uri.path, \"/e\"))"
    requests   = 30
    period     = 10
    block_for  = 10
  }]
}

output "site" { value = module.site }
