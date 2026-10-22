# Een extra domein dat alleen doorstuurt naar de site (bijvoorbeeld kleurhoek.be en kleurhoek.com naar
# www.kleurhoek.nl). Het pad en de query blijven behouden, zodat oude of gedeelde links blijven werken.
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
  rules = [{
    ref         = "redirect_domain"
    description = "${var.domain} en www.${var.domain} naar ${var.target}"
    expression  = "(http.host in {\"${var.domain}\" \"www.${var.domain}\"})"
    action      = "redirect"
    enabled     = true
    action_parameters = {
      from_value = {
        status_code           = 301
        preserve_query_string = true
        target_url = {
          expression = "concat(\"${var.target}\", http.request.uri.path)"
        }
      }
    }
  }]
}
