variable "environment" {
  type        = string
  description = "dev of prod"
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment is dev of prod"
  }
}

variable "location" {
  type    = string
  default = "germanywestcentral"
}

variable "tenant_id" {
  type        = string
  description = "Tenant van Kleurhoek in de database (TENANT_ID van de API)."
  default     = "0192f6a0-0000-7000-8000-000000000001"
}

variable "github_repository" {
  type        = string
  default     = "t-jarpis/kleurhoek"
  description = "Repo die via OIDC (zonder geheimen) mag deployen."
}

variable "hosts" {
  type = object({
    site  = string
    admin = string
  })
  description = "Hostnamen, bijvoorbeeld www.kleurhoek.nl en admin.kleurhoek.nl. De API heeft geen publieke hostnaam."
}

variable "markets" {
  type    = string
  default = "nl-nl"
}

variable "oidc" {
  type = object({
    issuer          = string
    project_id      = string
    site_org_id     = string
    admin_org_id    = string
    web_client_id   = string
    admin_client_id = string
  })
}

variable "oidc_client_secrets" {
  type = object({
    web   = string
    admin = string
  })
  sensitive = true
}

variable "admin_bootstrap_subjects" {
  type        = list(string)
  default     = []
  description = "Zitadel-ID's die bij hun eerste login platformbeheerder worden."
}

variable "postgres" {
  type = object({
    sku_name          = string
    storage_mb        = number
    high_availability = bool
    backup_days       = number
  })
  default = {
    sku_name          = "B_Standard_B1ms"
    storage_mb        = 32768
    high_availability = false
    backup_days       = 7
  }
}

variable "replicas" {
  type = object({
    api_min = number
    api_max = number
    web_min = number
    web_max = number
  })
  default = { api_min = 0, api_max = 3, web_min = 0, web_max = 3 }
}

variable "allowed_ingress_cidrs" {
  type        = list(string)
  description = "Alleen dit verkeer mag de apps bereiken: de IP-ranges van Cloudflare."
}

variable "origin_certificate" {
  type = object({
    certificate_pem = string
    private_key_pem = string
  })
  default     = null
  sensitive   = true
  description = "Cloudflare Origin CA-certificaat voor de eigen domeinen. Leeg = nog geen eigen domeinen."
}

variable "domain_records" {
  type        = map(string)
  default     = {}
  description = "Per app (web, admin) het ID van het asuid-TXT-record in Cloudflare. Pas als dat bestaat, wordt het domein gekoppeld."
}

variable "bootstrap_image" {
  type        = string
  default     = "mcr.microsoft.com/k8se/quickstart:latest"
  description = "Image voor de allereerste aanmaak. Daarna zet de deploy-workflow de echte images."
}

variable "tags" {
  type    = map(string)
  default = {}
}
