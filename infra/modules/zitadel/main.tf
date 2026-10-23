# Kleurhoek in Zitadel: de organisatie voor websitegebruikers, het project en twee apps (website en
# admin panel). De beheerorganisatie (Org Beheer, met verplichte passkeys) is gedeeld tussen sites en
# wordt in de platform-infra beheerd; hier krijgt die alleen toegang tot het project.

terraform {
  required_providers {
    zitadel = { source = "zitadel/zitadel", version = "~> 3.8" }
  }
}

variable "environment" { type = string }
variable "site_url" {
  type        = string
  description = "Bijvoorbeeld https://www.kleurhoek.nl"
}
variable "admin_url" {
  type        = string
  description = "Bijvoorbeeld https://admin.kleurhoek.nl"
}
variable "admin_org_id" {
  type        = string
  description = "Organisatie-ID van Org Beheer (gedeeld, uit de platform-infra)."
}
variable "local_development" {
  type        = bool
  default     = false
  description = "Alleen voor docker compose: http-redirects op localhost toestaan en geen MFA-vraag bij inloggen."
}
variable "login_base_uri" {
  type        = string
  default     = null
  description = "Eigen inlogpagina voor de website (login v2), bijvoorbeeld https://login.kleurhoek.nl. Leeg = de inlogpagina van Zitadel."
}
variable "idp_ids" {
  type        = list(string)
  default     = []
  description = "ID's van de identity providers (Google, Apple, Microsoft) op instance-niveau."
}

locals {
  suffix = var.environment == "prod" ? "" : " (${var.environment})"
}

resource "zitadel_org" "site" {
  name = "Kleurhoek${local.suffix}"
}

# Websitegebruikers: inloggen met Google, Apple of Microsoft, een passkey of een code per e-mail.
# Wachtwoorden zetten we uit in de login-instellingen van de instance (zie infra/README.md).
resource "zitadel_login_policy" "site" {
  org_id                        = zitadel_org.site.id
  user_login                    = true
  allow_register                = true
  allow_external_idp            = true
  idps                          = var.idp_ids
  force_mfa                     = false
  force_mfa_local_only          = false
  passwordless_type             = "PASSWORDLESS_TYPE_ALLOWED"
  hide_password_reset           = true
  ignore_unknown_usernames      = true
  allow_domain_discovery        = false
  disable_login_with_phone      = true
  default_redirect_uri          = var.site_url
  password_check_lifetime       = "240h0m0s"
  external_login_check_lifetime = "240h0m0s"
  mfa_init_skip_lifetime        = var.local_development ? "0s" : "720h0m0s"
  second_factor_check_lifetime  = "24h0m0s"
  multi_factor_check_lifetime   = "24h0m0s"
}

resource "zitadel_project" "kleurhoek" {
  org_id = zitadel_org.site.id
  name   = "Kleurhoek${local.suffix}"
  # Rechten bepaalt de API zelf; Zitadel zegt alleen wie iemand is.
  project_role_assertion = false
  project_role_check     = false
  has_project_check      = false
}

# Beheerders uit Org Beheer mogen inloggen op het admin panel van Kleurhoek.
resource "zitadel_project_grant" "beheer" {
  org_id         = zitadel_org.site.id
  project_id     = zitadel_project.kleurhoek.id
  granted_org_id = var.admin_org_id
}

# JWT-access tokens: de API controleert ze zelf met de publieke sleutels (geen introspectie per verzoek).
resource "zitadel_application_oidc" "web" {
  org_id                    = zitadel_org.site.id
  project_id                = zitadel_project.kleurhoek.id
  name                      = "Kleurhoek web"
  app_type                  = "OIDC_APP_TYPE_WEB"
  auth_method_type          = "OIDC_AUTH_METHOD_TYPE_BASIC"
  grant_types               = ["OIDC_GRANT_TYPE_AUTHORIZATION_CODE", "OIDC_GRANT_TYPE_REFRESH_TOKEN"]
  response_types            = ["OIDC_RESPONSE_TYPE_CODE"]
  redirect_uris             = ["${var.site_url}/auth/callback"]
  post_logout_redirect_uris = ["${var.site_url}/"]

  dynamic "login_version" {
    for_each = var.login_base_uri == null ? [] : [1]
    content {
      login_v2 {
        base_uri = var.login_base_uri
      }
    }
  }
  access_token_type           = "OIDC_TOKEN_TYPE_JWT"
  access_token_role_assertion = false
  id_token_userinfo_assertion = true
  dev_mode                    = var.local_development
  clock_skew                  = "0s"
}

resource "zitadel_application_oidc" "admin" {
  org_id                      = zitadel_org.site.id
  project_id                  = zitadel_project.kleurhoek.id
  name                        = "Kleurhoek admin"
  app_type                    = "OIDC_APP_TYPE_WEB"
  auth_method_type            = "OIDC_AUTH_METHOD_TYPE_BASIC"
  grant_types                 = ["OIDC_GRANT_TYPE_AUTHORIZATION_CODE", "OIDC_GRANT_TYPE_REFRESH_TOKEN"]
  response_types              = ["OIDC_RESPONSE_TYPE_CODE"]
  redirect_uris               = ["${var.admin_url}/auth/callback"]
  post_logout_redirect_uris   = ["${var.admin_url}/auth/uitgelogd"]
  access_token_type           = "OIDC_TOKEN_TYPE_JWT"
  access_token_role_assertion = false
  id_token_userinfo_assertion = true
  dev_mode                    = var.local_development
  clock_skew                  = "0s"
}

# ---------- Eigen inlogpagina (ADR 0018) ----------
# Een service user met de instance-rol IAM_LOGIN_CLIENT: alleen die mag sessies aanmaken, codes sturen,
# gebruikers registreren en een inlogpoging afronden. Het token gaat als geheim naar de container.
resource "zitadel_machine_user" "login" {
  org_id            = zitadel_org.site.id
  user_name         = "kleurhoek-login${var.environment == "prod" ? "" : "-${var.environment}"}"
  name              = "Kleurhoek inlogpagina${local.suffix}"
  description       = "Eigen inlogpagina van Kleurhoek (login v2, ADR 0018)"
  access_token_type = "ACCESS_TOKEN_TYPE_BEARER"
}

resource "zitadel_personal_access_token" "login" {
  org_id          = zitadel_org.site.id
  user_id         = zitadel_machine_user.login.id
  expiration_date = "2030-01-01T00:00:00Z"
}

resource "zitadel_instance_member" "login" {
  user_id = zitadel_machine_user.login.id
  roles   = ["IAM_LOGIN_CLIENT"]
}

output "login_token" {
  value     = zitadel_personal_access_token.login.token
  sensitive = true
}

output "site_org_id" { value = zitadel_org.site.id }
output "project_id" { value = zitadel_project.kleurhoek.id }
output "web_client_id" { value = zitadel_application_oidc.web.client_id }
output "admin_client_id" { value = zitadel_application_oidc.admin.client_id }
output "web_client_secret" {
  value     = zitadel_application_oidc.web.client_secret
  sensitive = true
}
output "admin_client_secret" {
  value     = zitadel_application_oidc.admin.client_secret
  sensitive = true
}
