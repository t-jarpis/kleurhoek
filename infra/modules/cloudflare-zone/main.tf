# Alles wat voor de hele zone kleurhoek.nl geldt, op één plek (envs/zone): TLS-instellingen, CAA,
# redirects, cache-regel, rate limits, het login-record en de geheime header per omgeving.
# Cloudflare kent per zone één ruleset per fase; zouden dev en prod die elk beheren, dan
# overschrijven ze elkaar. De omgevingen zelf beheren alleen hun eigen DNS-records en Access.

terraform {
  required_providers {
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 5.28" }
    random     = { source = "hashicorp/random", version = "~> 3.7" }
  }
}

variable "zone_id" { type = string }
variable "domain" {
  type        = string
  description = "Bijvoorbeeld kleurhoek.nl"
}
variable "environments" {
  type        = map(object({ site = string, admin = string }))
  description = "Subdomeinen per omgeving, bijvoorbeeld { dev = { site = \"dev\", admin = \"admin-dev\" } }."
}
variable "apex_redirect" {
  type        = bool
  default     = false
  description = "Kaal domein naar www (aanzetten zodra productie live is)."
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
  acme_path = "/.well-known/acme-challenge/"
  www       = "${var.environments["prod"].site}.${var.domain}"
  hosts = { for env, s in var.environments : env => [
    "${s.site}.${var.domain}",
    "${s.admin}.${var.domain}",
  ] }
}

# ---------- Geheime header per omgeving ----------
# Website en admin weigeren verzoeken zonder deze header: zo komt niemand via de standaard-hostnaam
# van Scaleway langs Cloudflare (WAF, rate limits, Access) heen.

resource "random_password" "edge" {
  for_each = var.environments
  length   = 48
  special  = false
}

resource "cloudflare_ruleset" "edge_header" {
  zone_id     = var.zone_id
  name        = "Kleurhoek edge-header"
  description = "Beheerd door Terraform"
  kind        = "zone"
  phase       = "http_request_late_transform"
  rules = [for env, hosts in local.hosts : {
    ref         = "edge_${env}"
    description = "Geheime header naar de origin (${env})"
    expression  = "(http.host in {${join(" ", [for h in hosts : "\"${h}\""])}})"
    action      = "rewrite"
    enabled     = true
    action_parameters = {
      headers = {
        "x-kleurhoek-edge" = { operation = "set", value = random_password.edge[env].result }
      }
    }
  }]
}

# ---------- TLS ----------
# Scaleway haalt per eigen domein een certificaat bij Let's Encrypt (HTTP-01). Die controle moet over
# gewoon HTTP en ongecachet tot aan de container komen. Daarom staat "Always Use HTTPS" uit en stuurt
# een eigen regel alles behalve /.well-known/acme-challenge/ naar HTTPS. Met TLS strict gebruikt
# Cloudflare richting origin hetzelfde schema als de bezoeker.

resource "cloudflare_zone_setting" "ssl" {
  zone_id    = var.zone_id
  setting_id = "ssl"
  value      = "strict"
}

resource "cloudflare_zone_setting" "https" {
  for_each = {
    always_use_https         = "off"
    automatic_https_rewrites = "on"
    min_tls_version          = "1.2"
    tls_1_3                  = "on"
  }
  zone_id    = var.zone_id
  setting_id = each.key
  value      = each.value
}

# Let's Encrypt mag certificaten uitgeven (Scaleway); Cloudflare voegt zijn eigen CA's zelf toe.
resource "cloudflare_dns_record" "caa" {
  zone_id = var.zone_id
  name    = "@"
  type    = "CAA"
  ttl     = 3600
  data = {
    flags = 0
    tag   = "issue"
    value = "letsencrypt.org"
  }
  comment = "Certificaten van Scaleway-containers (Terraform)"
}

resource "cloudflare_ruleset" "cache" {
  zone_id     = var.zone_id
  name        = "Kleurhoek cache"
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

# ---------- Redirects ----------

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

locals {
  redirect_rules = concat(
    var.apex_redirect ? [{
      ref         = "apex_to_www"
      description = "${var.domain} naar ${local.www}"
      expression  = "(http.host eq \"${var.domain}\")"
      target      = "concat(\"https://${local.www}\", http.request.uri.path)"
    }] : [],
    [{
      ref         = "https"
      description = "HTTP naar HTTPS, behalve de certificaatcontrole"
      expression  = "(not ssl and not starts_with(http.request.uri.path, \"${local.acme_path}\"))"
      target      = "concat(\"https://\", http.host, http.request.uri.path)"
    }],
  )
}

resource "cloudflare_ruleset" "redirects" {
  zone_id     = var.zone_id
  name        = "Kleurhoek redirects"
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

output "edge_secrets" {
  value     = { for env, p in random_password.edge : env => p.result }
  sensitive = true
}
