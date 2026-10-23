# Eén omgeving van Kleurhoek in Cloudflare: de DNS-records naar de Serverless Containers van Scaleway
# en Cloudflare Access voor het admin panel. Instellingen voor de hele zone (TLS, redirects, rate
# limits, de geheime header) staan in modules/cloudflare-zone (envs/zone).

terraform {
  required_providers {
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
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
variable "origin_hosts" {
  type        = map(string)
  description = "Standaard-hostnamen van de containers (web, admin). Leeg zolang de containers nog niet bestaan."
}
variable "admin_emails" {
  type        = list(string)
  description = "Wie langs Cloudflare Access naar het admin panel mag (daarna nog Zitadel met passkey)."
}

locals {
  site_host  = "${var.subdomains.site}.${var.domain}"
  admin_host = "${var.subdomains.admin}.${var.domain}"
  names      = { web = var.subdomains.site, admin = var.subdomains.admin }
}

# Proxied: bezoekers zien alleen Cloudflare. De origin weigert verzoeken zonder de geheime header.
resource "cloudflare_dns_record" "app" {
  for_each = var.origin_hosts
  zone_id  = var.zone_id
  name     = local.names[each.key]
  type     = "CNAME"
  content  = each.value
  proxied  = true
  ttl      = 1
  comment  = "Kleurhoek ${each.key} (Terraform)"
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

# Let's Encrypt controleert het admindomein via /.well-known/acme-challenge/. Zonder deze uitzondering
# stuurt Access die controle naar het inlogscherm, krijgt Scaleway geen certificaat en kan Cloudflare de
# admin niet bereiken (lege pagina na het inloggen). Alleen dit pad, voor iedereen; de rest blijft dicht.
resource "cloudflare_zero_trust_access_policy" "acme" {
  account_id = var.account_id
  name       = "Certificaatcontrole (${var.subdomains.admin})"
  decision   = "bypass"
  include    = [{ everyone = {} }]
}

resource "cloudflare_zero_trust_access_application" "acme" {
  account_id           = var.account_id
  name                 = "Kleurhoek admin certificaat (${var.subdomains.admin})"
  type                 = "self_hosted"
  domain               = "${local.admin_host}/.well-known/acme-challenge/"
  app_launcher_visible = false
  policies = [{
    id         = cloudflare_zero_trust_access_policy.acme.id
    precedence = 1
  }]
}

output "site_host" { value = local.site_host }
output "admin_host" { value = local.admin_host }

# Per app het ID van het CNAME-record: Scaleway koppelt het domein pas als dit bestaat.
output "domain_records" {
  value = { for k, r in cloudflare_dns_record.app : k => r.id }
  # Pas koppelen als de certificaatcontrole langs Access kan.
  depends_on = [cloudflare_zero_trust_access_application.acme]
}
