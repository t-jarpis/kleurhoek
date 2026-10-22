# Kleurhoek in Cloudflare: DNS naar Azure, TLS tot aan de origin, rate limits aan de rand,
# Cloudflare Access voor het admin panel en een redirect van het kale domein naar www.
# De zone zelf (kleurhoek.nl) wordt eenmalig met de hand aangemaakt bij het registreren van het domein.

terraform {
  required_providers {
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    tls        = { source = "hashicorp/tls", version = "~> 4.1" }
  }
}

variable "account_id" { type = string }
variable "zone_id" { type = string }
variable "domain" {
  type        = string
  description = "Bijvoorbeeld kleurhoek.nl"
}
variable "subdomains" {
  type        = object({ site = string, admin = string })
  description = "Bijvoorbeeld { site = \"www\", admin = \"admin\" }; in dev { site = \"dev\", admin = \"admin-dev\" }."
}
variable "origin_fqdns" {
  type        = object({ web = string, admin = string })
  description = "Standaard-hostnamen van de Container Apps."
}
variable "verification_id" {
  type        = string
  description = "custom_domain_verification_id van de Container Apps-omgeving."
}
variable "apex_redirect" {
  type        = bool
  default     = false
  description = "Alleen in productie: kleurhoek.nl stuurt door naar www."
}
variable "admin_emails" {
  type        = list(string)
  description = "Wie langs Cloudflare Access naar het admin panel mag (daarna nog Zitadel met passkey)."
}
variable "login_cname" {
  type        = string
  default     = null
  description = "Doel voor login.<domein> (het eigen domein van Zitadel Cloud). Leeg = geen record."
}
variable "edge_rate_limits" {
  type = list(object({
    name       = string
    expression = string
    requests   = number
    period     = number
    block_for  = number
  }))
  description = "Rate limits aan de rand. Het gratis plan staat één regel met period 10 toe; Pro meer."
}

locals {
  site_host  = "${var.subdomains.site}.${var.domain}"
  admin_host = "${var.subdomains.admin}.${var.domain}"
  records = {
    web   = { name = var.subdomains.site, target = var.origin_fqdns.web }
    admin = { name = var.subdomains.admin, target = var.origin_fqdns.admin }
  }
}

# Proxied: bezoekers zien alleen Cloudflare. De origin accepteert alleen Cloudflare-IP's (zie Azure).
resource "cloudflare_dns_record" "app" {
  for_each = local.records
  zone_id  = var.zone_id
  name     = each.value.name
  type     = "CNAME"
  content  = each.value.target
  proxied  = true
  ttl      = 1
  comment  = "Kleurhoek ${each.key} (Terraform)"
}

# Bewijs voor Azure dat wij het domein beheren.
resource "cloudflare_dns_record" "asuid" {
  for_each = local.records
  zone_id  = var.zone_id
  name     = "asuid.${each.value.name}"
  type     = "TXT"
  content  = "\"${var.verification_id}\""
  ttl      = 3600
  comment  = "Azure Container Apps domeinverificatie (Terraform)"
}

resource "cloudflare_dns_record" "login" {
  count   = var.login_cname == null ? 0 : 1
  zone_id = var.zone_id
  name    = "login"
  type    = "CNAME"
  content = var.login_cname
  proxied = false
  ttl     = 3600
  comment = "Zitadel Cloud (Terraform)"
}

# ---------- TLS tot aan de origin ----------

resource "tls_private_key" "origin" {
  algorithm   = "ECDSA"
  ecdsa_curve = "P256"
}

resource "tls_cert_request" "origin" {
  private_key_pem = tls_private_key.origin.private_key_pem
  subject {
    common_name  = local.site_host
    organization = "Kleurhoek"
  }
}

resource "cloudflare_origin_ca_certificate" "origin" {
  csr                = tls_cert_request.origin.cert_request_pem
  hostnames          = sort([local.site_host, local.admin_host]) # Cloudflare geeft ze gesorteerd terug
  request_type       = "origin-ecc"
  requested_validity = 5475
}

resource "cloudflare_zone_setting" "ssl" {
  zone_id    = var.zone_id
  setting_id = "ssl"
  value      = "strict"
}

resource "cloudflare_zone_setting" "https" {
  for_each = {
    always_use_https         = "on"
    automatic_https_rewrites = "on"
    min_tls_version          = "1.2"
    tls_1_3                  = "on"
  }
  zone_id    = var.zone_id
  setting_id = each.key
  value      = each.value
}

# ---------- Rate limits aan de rand ----------
# Grof en goedkoop: tegen floods. De fijne, per-endpoint limieten zitten in de API (instelbaar in het admin panel).

resource "cloudflare_ruleset" "rate_limits" {
  zone_id     = var.zone_id
  name        = "Kleurhoek rate limits"
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

# ---------- Kaal domein naar www ----------

resource "cloudflare_dns_record" "apex" {
  count   = var.apex_redirect ? 1 : 0
  zone_id = var.zone_id
  name    = "@"
  type    = "A"
  content = "192.0.2.1"
  proxied = true
  ttl     = 1
  comment = "Alleen voor de redirect naar www (Terraform)"
}

resource "cloudflare_ruleset" "apex_redirect" {
  count       = var.apex_redirect ? 1 : 0
  zone_id     = var.zone_id
  name        = "Kaal domein naar www"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_dynamic_redirect"
  rules = [{
    ref         = "apex_to_www"
    description = "${var.domain} naar ${local.site_host}"
    expression  = "(http.host eq \"${var.domain}\")"
    action      = "redirect"
    enabled     = true
    action_parameters = {
      from_value = {
        status_code           = 301
        preserve_query_string = true
        target_url = {
          expression = "concat(\"https://${local.site_host}\", http.request.uri.path)"
        }
      }
    }
  }]
}

# ---------- Admin panel achter Cloudflare Access ----------
# Twee sloten: eerst Cloudflare Access (e-mailcode, 8 uur), daarna Zitadel met passkey.

resource "cloudflare_zero_trust_access_policy" "admins" {
  account_id = var.account_id
  name       = "Kleurhoek beheerders (${var.subdomains.admin})"
  decision   = "allow"
  include    = [for e in var.admin_emails : { email = { email = e } }]
}

resource "cloudflare_zero_trust_access_application" "admin" {
  account_id                 = var.account_id
  name                       = "Kleurhoek admin (${var.subdomains.admin})"
  type                       = "self_hosted"
  domain                     = local.admin_host
  session_duration           = "8h"
  app_launcher_visible       = false
  http_only_cookie_attribute = true
  policies = [{
    id         = cloudflare_zero_trust_access_policy.admins.id
    precedence = 1
  }]
}

output "site_host" { value = local.site_host }
output "admin_host" { value = local.admin_host }

# Per app het ID van het asuid-record: Azure koppelt het domein pas als dit bestaat.
output "domain_records" {
  value = { for k, r in cloudflare_dns_record.asuid : k => r.id }
}

output "origin_certificate" {
  value = {
    certificate_pem = cloudflare_origin_ca_certificate.origin.certificate
    private_key_pem = tls_private_key.origin.private_key_pem
  }
  sensitive = true
}
