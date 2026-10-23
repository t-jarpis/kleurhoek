variable "environment" {
  type        = string
  description = "dev of prod"
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment is dev of prod"
  }
}

variable "tenant_id" {
  type        = string
  description = "Tenant van Kleurhoek in de database (TENANT_ID van de API)."
  default     = "0192f6a0-0000-7000-8000-000000000001"
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

variable "database" {
  type = object({
    node_type      = string # bijvoorbeeld DB-PLAY2-PICO; zie `scw rdb node-type list`
    engine         = string # bijvoorbeeld PostgreSQL-16; zie `scw rdb engine list`
    volume_gb      = number
    ha             = bool
    backup_days    = number
    backup_hours   = number
    backup_same_dc = bool
  })
}

variable "scale" {
  type = object({
    api_min = number
    api_max = number
    web_min = number
    web_max = number
  })
  default = { api_min = 0, api_max = 3, web_min = 0, web_max = 3 }
}

variable "apps_enabled" {
  type        = bool
  default     = true
  description = "False bij de allereerste apply: dan bestaan de images nog niet. Zie infra/README.md."
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
  description = "Header-waarde die Cloudflare meestuurt; website en admin weigeren verzoeken zonder (alleen via Cloudflare)."
}

variable "domain_records" {
  type        = map(string)
  default     = {}
  description = "Per app (web, admin) het ID van het CNAME-record in Cloudflare. Pas als dat bestaat, wordt het domein gekoppeld."
}

variable "tags" {
  type    = list(string)
  default = []
}
