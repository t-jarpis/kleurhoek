# Eén omgeving van Kleurhoek: Zitadel, Scaleway en Cloudflare samen. envs/dev en envs/prod roepen dit
# aan met hun eigen waarden; zo lopen de omgevingen niet uit elkaar.

terraform {
  required_providers {
    scaleway   = { source = "scaleway/scaleway", version = "~> 2.88" }
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    zitadel    = { source = "zitadel/zitadel", version = "~> 3.8" }
  }
}

variable "environment" { type = string }
variable "domain" { type = string }
variable "subdomains" { type = object({ site = string, admin = string, login = string }) }
variable "own_login" {
  type        = bool
  default     = true
  description = "De website laat inloggen via de eigen inlogpagina (ADR 0018). False = terug naar de inlogpagina van Zitadel."
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
variable "admin_emails" { type = list(string) }
variable "admin_bootstrap_subjects" {
  type    = list(string)
  default = []
}
variable "database" {
  type = object({
    node_type      = string
    engine         = string
    volume_gb      = number
    ha             = bool
    backup_days    = number
    backup_hours   = number
    backup_same_dc = bool
  })
}
variable "scale" {
  type = object({ api_min = number, api_max = number, web_min = number, web_max = number })
}
variable "apps_enabled" {
  type        = bool
  default     = true
  description = "False bij de allereerste apply (er zijn nog geen images). Zie infra/README.md."
}
variable "markets" {
  type        = string
  default     = "nl-nl,nl-be,fr-be,en-gb,de-de,de-at,de-ch,fr-fr,fr-ch,en-us,en-ie,es-es,it-it,pl-pl,en-ca,en-au,en-nz,fr-ca,fr-lu,de-lu,de-li,it-ch,es-mx,es-ar,es-co,es-us,pt-br,pt-pt,sv-se,da-dk,nb-no,fi-fi,cs-cz,sk-sk,hu-hu,ro-ro,ro-md,el-gr,el-cy,en-mt,fr-mc,es-ad,it-sm,bg-bg,hr-hr,hr-ba,hr-me,sl-si,et-ee,lv-lv,lt-lt,uk-ua,tr-tr"
  description = "Markten die live staan, komma-gescheiden."
}
variable "market_domains" {
  type        = list(string)
  default     = []
  description = "Domeinen per land naast het hoofddomein (ADR 0040), bijvoorbeeld [\"kleurhoek.be\", \"kleurhoek.com\"]. Leeg = alles op het hoofddomein met /<markt>."
}
variable "search" {
  type = object({
    google_key_file = optional(string, "")
    bing_api_key    = optional(string, "")
  })
  sensitive   = true
  default     = {}
  description = "Zoekcijfers (ADR 0041): pad naar de JSON-sleutel van het Google-serviceaccount en de API-sleutel van Bing Webmaster Tools."
}
variable "mail" {
  type = object({
    from                   = string
    smtp_url               = optional(string, "")
    transactional_smtp_url = optional(string, "")
  })
  sensitive   = true
  default     = { from = "Kleurhoek <hallo@kleurhoek.nl>" }
  description = "Mail (ADR 0037): afzender en SMTP-adressen (smtp://gebruiker:wachtwoord@host:587). Leeg = versturen staat uit."
}
variable "org_host_pattern" {
  type        = string
  description = "Subdomein van een organisatie, met {slug} voor de code. Dev: {slug}-dev.kleurhoek.nl, prod: {slug}.kleurhoek.nl (ADR 0017)."
}
variable "org_worker_secret" {
  type        = string
  sensitive   = true
  description = "Geheim van de Worker voor organisatiedomeinen (uit envs/zone); alleen dan vertrouwt de website de doorgegeven host en IP."
}
variable "edge_secret" {
  type        = string
  sensitive   = true
  description = "Geheime header-waarde van deze omgeving, uit envs/zone."
}

locals {
  hosts = {
    site  = "${var.subdomains.site}.${var.domain}"
    admin = "${var.subdomains.admin}.${var.domain}"
    login = "${var.subdomains.login}.${var.domain}"
  }
  site_url  = "https://${local.hosts.site}"
  admin_url = "https://${local.hosts.admin}"
  # Domeinen per land (ADR 0040): zelfde subdomein (www of dev) op kleurhoek.be en kleurhoek.com.
  market_urls  = { for d in var.market_domains : d => "https://${var.subdomains.site}.${d}" }
  site_domains = length(var.market_domains) == 0 ? "" : jsonencode({ nl = local.site_url, be = local.market_urls["kleurhoek.be"], com = local.market_urls["kleurhoek.com"] })
}

module "zitadel" {
  source       = "../zitadel"
  environment  = var.environment
  site_url     = local.site_url
  site_aliases = values(local.market_urls)
  admin_url    = local.admin_url
  admin_org_id = var.zitadel_admin_org_id
  idp_ids      = var.zitadel_idp_ids
  # Website via de eigen inlogpagina; het admin panel blijft (voorlopig) op de inlogpagina van Zitadel.
  login_base_uri = var.own_login ? "https://${local.hosts.login}" : null
}

module "scaleway" {
  source         = "../scaleway"
  environment    = var.environment
  hosts          = local.hosts
  markets        = var.markets
  site_domains   = local.site_domains
  search_domains = var.environment == "prod" ? concat([var.domain], var.market_domains) : []
  search = {
    google_key = nonsensitive(var.search.google_key_file) != "" ? file(pathexpand(var.search.google_key_file)) : ""
    bing_key   = var.search.bing_api_key
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
  database                 = var.database
  scale                    = var.scale
  apps_enabled             = var.apps_enabled
  edge_secret              = var.edge_secret
  zitadel_login_token      = module.zitadel.login_token
  passkey_domain           = var.domain
  org_host_pattern         = var.org_host_pattern
  mail                     = var.mail
  org_worker_secret        = var.org_worker_secret
  domain_records           = module.cloudflare.domain_records
}

module "cloudflare" {
  source       = "../cloudflare"
  account_id   = var.cloudflare_account_id
  zone_id      = var.cloudflare_zone_id
  domain       = var.domain
  subdomains   = var.subdomains
  origin_hosts = module.scaleway.public_hosts
  admin_emails = var.admin_emails
}

output "site_url" { value = local.site_url }
output "admin_url" { value = local.admin_url }
output "registry_endpoint" { value = module.scaleway.registry_endpoint }
output "container_ids" { value = module.scaleway.container_ids }

# Alles wat de GitHub-omgeving nodig heeft. Gevoelig: lees met `terraform output -json github`.
output "github" {
  value = {
    variables = {
      SCW_ACCESS_KEY = module.scaleway.github_deploy.access_key
      SCW_PROJECT_ID = module.scaleway.github_deploy.project_id
      LOGS_URL       = module.scaleway.github_deploy.logs_url
      SCW_REGION     = "nl-ams"
      REGISTRY       = module.scaleway.registry_endpoint
      CONTAINER_IDS  = jsonencode(module.scaleway.container_ids)
      SITE_URL       = local.site_url
      MARKETS        = var.markets
    }
    secrets = {
      SCW_SECRET_KEY = module.scaleway.github_deploy.secret_key
      LOGS_TOKEN     = module.scaleway.github_deploy.logs_token
      SITE_CHECK_KEY = module.scaleway.github_deploy.site_check_key
    }
  }
  sensitive = true
}
