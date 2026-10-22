# Eén omgeving van Kleurhoek: Zitadel, Azure en Cloudflare samen. envs/dev en envs/prod roepen dit
# aan met hun eigen waarden; zo lopen de omgevingen niet uit elkaar.

terraform {
  required_providers {
    azurerm    = { source = "hashicorp/azurerm", version = "~> 5.10" }
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    zitadel    = { source = "zitadel/zitadel", version = "~> 3.8" }
  }
}

variable "environment" { type = string }
variable "domain" { type = string }
variable "subdomains" { type = object({ site = string, admin = string }) }
variable "apex_redirect" {
  type    = bool
  default = false
}
variable "cloudflare_account_id" { type = string }
variable "cloudflare_zone_id" { type = string }
variable "zitadel_issuer" {
  type        = string
  description = "Bijvoorbeeld https://login.kleurhoek.nl"
}
variable "zitadel_admin_org_id" { type = string }
variable "zitadel_idp_ids" {
  type    = list(string)
  default = []
}
variable "zitadel_login_cname" {
  type    = string
  default = null
}
variable "admin_emails" { type = list(string) }
variable "admin_bootstrap_subjects" {
  type    = list(string)
  default = []
}
variable "postgres" {
  type = object({
    sku_name          = string
    storage_mb        = number
    high_availability = bool
    backup_days       = number
  })
}
variable "replicas" {
  type = object({ api_min = number, api_max = number, web_min = number, web_max = number })
}
variable "edge_rate_limits" {
  type = list(object({ name = string, expression = string, requests = number, period = number, block_for = number }))
}

data "cloudflare_ip_ranges" "cloudflare" {}

locals {
  site_url  = "https://${var.subdomains.site}.${var.domain}"
  admin_url = "https://${var.subdomains.admin}.${var.domain}"
}

module "zitadel" {
  source       = "../zitadel"
  environment  = var.environment
  site_url     = local.site_url
  admin_url    = local.admin_url
  admin_org_id = var.zitadel_admin_org_id
  idp_ids      = var.zitadel_idp_ids
}

module "azure" {
  source      = "../azure"
  environment = var.environment
  hosts = {
    site  = "${var.subdomains.site}.${var.domain}"
    admin = "${var.subdomains.admin}.${var.domain}"
  }
  oidc = {
    issuer          = var.zitadel_issuer
    project_id      = module.zitadel.project_id
    site_org_id     = module.zitadel.site_org_id
    admin_org_id    = var.zitadel_admin_org_id
    web_client_id   = module.zitadel.web_client_id
    admin_client_id = module.zitadel.admin_client_id
  }
  oidc_client_secrets = {
    web   = module.zitadel.web_client_secret
    admin = module.zitadel.admin_client_secret
  }
  admin_bootstrap_subjects = var.admin_bootstrap_subjects
  postgres                 = var.postgres
  replicas                 = var.replicas
  allowed_ingress_cidrs    = data.cloudflare_ip_ranges.cloudflare.ipv4_cidrs
  origin_certificate       = module.cloudflare.origin_certificate
  domain_records           = module.cloudflare.domain_records
}

module "cloudflare" {
  source           = "../cloudflare"
  account_id       = var.cloudflare_account_id
  zone_id          = var.cloudflare_zone_id
  domain           = var.domain
  subdomains       = var.subdomains
  apex_redirect    = var.apex_redirect
  origin_fqdns     = module.azure.app_fqdns
  verification_id  = module.azure.environment_verification_id
  admin_emails     = var.admin_emails
  login_cname      = var.zitadel_login_cname
  edge_rate_limits = var.edge_rate_limits
}

output "site_url" { value = local.site_url }
output "admin_url" { value = local.admin_url }
output "resource_group_name" { value = module.azure.resource_group_name }
output "acr_name" { value = module.azure.acr_name }
output "acr_login_server" { value = module.azure.acr_login_server }
output "app_names" { value = module.azure.app_names }
output "job_names" { value = module.azure.job_names }
output "github_deploy" { value = module.azure.github_deploy }
