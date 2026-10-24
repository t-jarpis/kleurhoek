# Een extra domein dat alleen doorstuurt naar de site (bijvoorbeeld kleurhoek.be en kleurhoek.com naar
# www.kleurhoek.nl). Het pad en de query blijven behouden, zodat oude of gedeelde links blijven werken.
# De doorverwijzing krijgt ?via=<code> mee, zodat de site kan tellen via welk domein iemand binnenkwam
# (ADR 0032); de site haalt die parameter na het tellen weer uit de adresbalk.
# De zone zelf wordt eenmalig met de hand aangemaakt in Cloudflare (nameservers bij de registrar).
# Krijgt een markt later een eigen domein (bijvoorbeeld nl-BE op kleurhoek.be), dan vervalt deze redirect.

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
variable "via" {
  type        = string
  description = "Code voor de telling van binnenkomsten, bijvoorbeeld be of com (ADR 0032)"
  validation {
    condition     = can(regex("^[a-z]{2,8}$", var.via))
    error_message = "Gebruik 2 tot 8 kleine letters."
  }
}
variable "target" {
  type        = string
  description = "Waarheen, zonder slash aan het eind. Bijvoorbeeld https://www.kleurhoek.nl"
}

locals {
  hosts = toset(["@", "www"])
}

# Proxied placeholder-records: Cloudflare beantwoordt het verzoek zelf met de redirect.
resource "cloudflare_dns_record" "redirect" {
  for_each = local.hosts
  zone_id  = var.zone_id
  name     = each.key
  type     = "A"
  content  = "192.0.2.1"
  proxied  = true
  ttl      = 1
  comment  = "Alleen voor de redirect naar ${var.target} (Terraform)"
}

resource "cloudflare_zone_setting" "https" {
  zone_id    = var.zone_id
  setting_id = "always_use_https"
  value      = "on"
}

resource "cloudflare_ruleset" "redirect" {
  zone_id     = var.zone_id
  name        = "${var.domain} doorsturen"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"
  # Twee regels: zonder query krijgt de doorverwijzing ?via=, met query wordt &via= achter de bestaande query gezet.
  rules = [
    {
      ref         = "redirect_domain"
      description = "${var.domain} en www.${var.domain} naar ${var.target} (zonder query)"
      expression  = "(http.host in {\"${var.domain}\" \"www.${var.domain}\"} and len(http.request.uri.query) eq 0)"
      action      = "redirect"
      enabled     = true
      action_parameters = {
        from_value = {
          status_code           = 301
          preserve_query_string = false
          target_url = {
            expression = "concat(\"${var.target}\", http.request.uri.path, \"?via=${var.via}\")"
          }
        }
      }
    },
    {
      ref         = "redirect_domain_query"
      description = "${var.domain} en www.${var.domain} naar ${var.target} (met query)"
      expression  = "(http.host in {\"${var.domain}\" \"www.${var.domain}\"} and len(http.request.uri.query) gt 0)"
      action      = "redirect"
      enabled     = true
      action_parameters = {
        from_value = {
          status_code           = 301
          preserve_query_string = false
          target_url = {
            expression = "concat(\"${var.target}\", http.request.uri.path, \"?\", http.request.uri.query, \"&via=${var.via}\")"
          }
        }
      }
    },
  ]
}
