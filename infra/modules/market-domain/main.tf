# Een eigen domein per land (ADR 0040): kleurhoek.be (nl-BE op /nl, fr-BE op /fr) en kleurhoek.com (andere
# markten op /<markt>). Ze tonen dezelfde website als kleurhoek.nl: www en dev wijzen rechtstreeks naar de
# website-container van de omgeving (ADR 0071; tot dan via de Worker, ADR 0040). De website kiest op de host
# de markten. Het kale domein stuurt door naar www. De zone zelf wordt eenmalig met de hand aangemaakt in
# Cloudflare (nameservers bij de registrar). Vervangt de oude module redirect-domain.

terraform {
  required_providers {
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
  }
}

variable "zone_id" { type = string }
variable "domain" {
  type        = string
  description = "Bijvoorbeeld kleurhoek.be"
}
variable "hosts" {
  type        = map(string)
  description = "Subdomein → omgeving, bijvoorbeeld { www = \"prod\", dev = \"dev\" }."
}
variable "edge_secrets" {
  type        = map(string)
  sensitive   = true
  description = "Geheime header per omgeving (uit modules/cloudflare-zone): de website weigert verzoeken zonder."
}
variable "edge_rate_limits" {
  type        = list(object({ name = string, expression = string, requests = number, period = number, block_for = number }))
  default     = []
  description = "Rate limits aan de rand, zoals op kleurhoek.nl (gratis plan: één regel, period 10)."
}
variable "apex_redirect" {
  type        = bool
  default     = true
  description = "Kaal domein naar www (alleen als www bestaat)."
}
variable "block_ai_bots" {
  type    = bool
  default = true
}
variable "txt_records" {
  type        = list(string)
  default     = []
  description = "TXT-records op het kale domein, bijvoorbeeld google-site-verification=… voor Search Console (ADR 0041)."
}

# www/dev.<domein> zelf staan in de omgevingen (modules/cloudflare en scaleway): een CNAME naar de
# website-container, met een eigen domein en certificaat daar (ADR 0071). Hier alles voor de hele zone.

locals {
  acme_path = "/.well-known/acme-challenge/"
  # Per omgeving de hosts op dit domein, voor de geheime header.
  env_hosts = { for env in distinct(values(var.hosts)) : env => [for sub, e in var.hosts : "${sub}.${var.domain}" if e == env] }
}

resource "cloudflare_dns_record" "apex" {
  count   = var.apex_redirect ? 1 : 0
  zone_id = var.zone_id
  name    = "@"
  type    = "A"
  content = "192.0.2.1"
  proxied = true
  ttl     = 1
  comment = "Alleen voor de redirect naar www.${var.domain} (Terraform)"
}

resource "cloudflare_dns_record" "txt" {
  for_each = toset(var.txt_records)
  zone_id  = var.zone_id
  name     = "@"
  type     = "TXT"
  content  = "\"${each.value}\""
  ttl      = 3600
  comment  = "Verificatie zoekmachines (Terraform)"
}

# Scaleway haalt per eigen domein een certificaat bij Let's Encrypt (HTTP-01). Die controle moet over gewoon
# HTTP en ongecachet tot aan de container komen; daarom Always Use HTTPS uit en een eigen regel naar HTTPS.
resource "cloudflare_zone_setting" "https" {
  for_each   = { always_use_https = "off", ssl = "strict", min_tls_version = "1.2" }
  zone_id    = var.zone_id
  setting_id = each.key
  value      = each.value
}

locals {
  redirect_rules = concat(
    var.apex_redirect ? [{
      ref         = "apex_to_www"
      description = "${var.domain} naar www.${var.domain}"
      expression  = "(http.host eq \"${var.domain}\")"
      target      = "concat(\"https://www.${var.domain}\", http.request.uri.path)"
    }] : [],
    [{
      ref         = "https"
      description = "HTTP naar HTTPS, behalve de certificaatcontrole"
      expression  = "(not ssl and not starts_with(http.request.uri.path, \"${local.acme_path}\"))"
      target      = "concat(\"https://\", http.host, http.request.uri.path)"
    }],
  )
}

resource "cloudflare_ruleset" "redirect" {
  zone_id     = var.zone_id
  name        = "${var.domain} redirects"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"
  rules = [for r in local.redirect_rules : {
    ref         = r.ref
    description = r.description
    expression  = r.expression
    action      = "redirect"
    enabled     = true
    action_parameters = {
      from_value = {
        status_code           = 301
        preserve_query_string = true
        target_url            = { expression = r.target }
      }
    }
  }]
}

resource "cloudflare_ruleset" "cache" {
  zone_id     = var.zone_id
  name        = "${var.domain} cache"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_cache_settings"
  rules = [{
    ref               = "acme_no_cache"
    description       = "Certificaatcontrole nooit cachen"
    expression        = "(starts_with(http.request.uri.path, \"${local.acme_path}\"))"
    action            = "set_cache_settings"
    enabled           = true
    action_parameters = { cache = false }
  }]
}

# Geheime header naar de origin, per omgeving (zoals op kleurhoek.nl): zonder weigert de website het verzoek.
resource "cloudflare_ruleset" "edge_header" {
  zone_id     = var.zone_id
  name        = "${var.domain} edge-header"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_late_transform"
  rules = [for env, hosts in local.env_hosts : {
    ref         = "edge_${env}"
    description = "Geheime header naar de origin (${env})"
    expression  = "(http.host in {${join(" ", [for h in hosts : "\"${h}\""])}})"
    action      = "rewrite"
    enabled     = true
    action_parameters = {
      headers = {
        "x-kleurhoek-edge" = { operation = "set", value = var.edge_secrets[env] }
      }
    }
  }]
}

resource "cloudflare_ruleset" "rate_limits" {
  count       = length(var.edge_rate_limits) > 0 ? 1 : 0
  zone_id     = var.zone_id
  name        = "${var.domain} rate limits"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_ratelimit"
  rules = [for r in var.edge_rate_limits : {
    ref         = r.name
    description = r.name
    expression  = r.expression
    action      = "block"
    enabled     = true
    ratelimit = {
      characteristics     = ["ip.src", "cf.colo.id"]
      period              = r.period
      requests_per_period = r.requests
      mitigation_timeout  = r.block_for
    }
  }]
}

# AI-crawlers ook op dit domein blokkeren (ADR 0045); bewust geen Bot Fight Mode.
resource "cloudflare_bot_management" "main" {
  count              = var.block_ai_bots ? 1 : 0
  zone_id            = var.zone_id
  ai_bots_protection = "block"
  fight_mode         = false
}

output "hosts" {
  value = { for sub, env in var.hosts : "${sub}.${var.domain}" => env }
}

# Overgenomen uit de oude module redirect-domain (zie envs/zone): dezelfde records en regels, nu bijgewerkt.
moved {
  from = cloudflare_dns_record.redirect["@"]
  to   = cloudflare_dns_record.apex[0]
}
moved {
  from = cloudflare_zone_setting.https
  to   = cloudflare_zone_setting.https["always_use_https"]
}
moved {
  from = cloudflare_ruleset.redirect[0]
  to   = cloudflare_ruleset.redirect
}
