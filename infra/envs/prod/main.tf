# Omgeving: prod. Draaien: zie infra/README.md.

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
    key                 = "kleurhoek-prod.tfstate"
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

variable "redirect_zone_ids" {
  type        = map(string)
  default     = {}
  description = "Extra domeinen die doorsturen naar www.kleurhoek.nl, met hun Cloudflare-zone-ID. Bijvoorbeeld { \"kleurhoek.be\" = \"...\", \"kleurhoek.com\" = \"...\" }."
}

variable "zitadel_login_cname" {
  type    = string
  default = null
}

module "site" {
  source                   = "../../modules/site"
  environment              = "prod"
  domain                   = "kleurhoek.nl"
  subdomains               = { site = "www", admin = "admin" }
  apex_redirect            = true
  cloudflare_account_id    = var.cloudflare_account_id
  cloudflare_zone_id       = var.cloudflare_zone_id
  zitadel_issuer           = "https://${var.zitadel_domain}"
  zitadel_admin_org_id     = var.zitadel_admin_org_id
  zitadel_idp_ids          = var.zitadel_idp_ids
  zitadel_login_cname      = var.zitadel_login_cname
  admin_emails             = var.admin_emails
  admin_bootstrap_subjects = var.admin_bootstrap_subjects
  postgres = {
    sku_name          = "GP_Standard_D2ds_v5"
    storage_mb        = 65536
    high_availability = true
    backup_days       = 35
  }
  # Altijd minstens één replica warm: geen koude start voor bezoekers.
  replicas = { api_min = 1, api_max = 6, web_min = 1, web_max = 10 }
  # Pro-plan: meerdere regels met een venster van een minuut.
  edge_rate_limits = [
    {
      name       = "inloggen"
      expression = "(starts_with(http.request.uri.path, \"/auth/\"))"
      requests   = 30
      period     = 60
      block_for  = 600
    },
    {
      name       = "analytics"
      expression = "(http.request.uri.path eq \"/e\")"
      requests   = 240
      period     = 60
      block_for  = 60
    },
  ]
}

# kleurhoek.be en kleurhoek.com sturen voorlopig door naar de Nederlandse site (pad blijft behouden).
# Gaat een markt live met een eigen domein, dan krijgt dat domein een eigen site-configuratie (ADR 0013).
module "redirect_domain" {
  source   = "../../modules/redirect-domain"
  for_each = var.redirect_zone_ids
  zone_id  = each.value
  domain   = each.key
  target   = "https://www.kleurhoek.nl"
}

output "site" { value = module.site }
