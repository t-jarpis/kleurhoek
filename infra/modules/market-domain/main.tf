# Een eigen domein per land (ADR 0040): kleurhoek.be (nl-BE op /nl, fr-BE op /fr) en kleurhoek.com (andere
# markten op /<markt>). Ze tonen dezelfde website als kleurhoek.nl, via de Worker kleurhoek-organisaties: die
# stuurt het verzoek naar de website van de omgeving en geeft de echte host mee. De website kiest op de host
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
variable "worker" {
  type        = string
  description = "Naam van de Worker die het verkeer doorstuurt (kleurhoek-organisaties)."
}
variable "apex_redirect" {
  type        = bool
  default     = true
  description = "Kaal domein naar www (alleen als www bestaat)."
}
variable "txt_records" {
  type        = list(string)
  default     = []
  description = "TXT-records op het kale domein, bijvoorbeeld google-site-verification=… voor Search Console (ADR 0041)."
}

# Proxied placeholder-records: Cloudflare stuurt het verzoek naar de Worker (of beantwoordt de redirect).
resource "cloudflare_dns_record" "site" {
  for_each = var.hosts
  zone_id  = var.zone_id
  name     = each.key
  type     = "AAAA"
  content  = "100::"
  proxied  = true
  ttl      = 1
  comment  = "Website (${each.value}) via de Worker ${var.worker} (Terraform)"
}

resource "cloudflare_workers_route" "site" {
  for_each = var.hosts
  zone_id  = var.zone_id
  pattern  = "${each.key}.${var.domain}/*"
  script   = var.worker
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

resource "cloudflare_zone_setting" "https" {
  for_each   = { always_use_https = "on", ssl = "strict", min_tls_version = "1.2" }
  zone_id    = var.zone_id
  setting_id = each.key
  value      = each.value
}

resource "cloudflare_ruleset" "redirect" {
  count       = var.apex_redirect ? 1 : 0
  zone_id     = var.zone_id
  name        = "${var.domain} naar www"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"
  rules = [{
    ref         = "apex_to_www"
    description = "${var.domain} naar www.${var.domain}"
    expression  = "(http.host eq \"${var.domain}\")"
    action      = "redirect"
    enabled     = true
    action_parameters = {
      from_value = {
        status_code           = 301
        preserve_query_string = true
        target_url            = { expression = "concat(\"https://www.${var.domain}\", http.request.uri.path)" }
      }
    }
  }]
}

output "hosts" {
  value = { for sub, env in var.hosts : "${sub}.${var.domain}" => env }
}

# Overgenomen uit de oude module redirect-domain (zie envs/zone): dezelfde records en regels, nu bijgewerkt.
moved {
  from = cloudflare_dns_record.redirect["www"]
  to   = cloudflare_dns_record.site["www"]
}
moved {
  from = cloudflare_dns_record.redirect["@"]
  to   = cloudflare_dns_record.apex[0]
}
moved {
  from = cloudflare_zone_setting.https
  to   = cloudflare_zone_setting.https["always_use_https"]
}
moved {
  from = cloudflare_ruleset.redirect
  to   = cloudflare_ruleset.redirect[0]
}
