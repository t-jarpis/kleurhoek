# Lokale omgeving voor docker compose: richt de Zitadel in de container in met dezelfde module als
# dev en prod, plus een beheerorganisatie en testaccounts. Draait automatisch in de dienst
# "zitadel-setup"; de uitkomst (client-ID's, geheimen) gaat als env-bestanden naar de apps.
# Alleen voor je eigen machine: wachtwoorden en geheimen hieronder zijn bewust niet geheim.

terraform {
  required_version = ">= 1.10"
  required_providers {
    zitadel = { source = "zitadel/zitadel", version = "~> 3.8" }
    local   = { source = "hashicorp/local", version = "~> 2.9" }
  }
  backend "local" {
    path = "/state/terraform.tfstate"
  }
}

variable "zitadel_pat_file" {
  type    = string
  default = "/zitadel-bootstrap/terraform.pat"
}
variable "output_dir" {
  type    = string
  default = "/bootstrap"
}

provider "zitadel" {
  domain       = "localhost"
  port         = "8080"
  insecure     = true
  access_token = trimspace(file(var.zitadel_pat_file))
}

locals {
  issuer    = "http://localhost:8080"
  site_url  = "http://localhost:3000"
  admin_url = "http://localhost:3002"
  password  = "Kleurhoek-lokaal-1!"
}

# In prod is Org Beheer gedeeld en staat hij in de platform-infra; lokaal maken we hem hier.
resource "zitadel_org" "beheer" {
  name = "Beheer (lokaal)"
}

resource "zitadel_login_policy" "beheer" {
  org_id                        = zitadel_org.beheer.id
  user_login                    = true
  allow_register                = false
  allow_external_idp            = false
  force_mfa                     = false
  force_mfa_local_only          = false
  passwordless_type             = "PASSWORDLESS_TYPE_ALLOWED"
  hide_password_reset           = true
  ignore_unknown_usernames      = true
  allow_domain_discovery        = false
  disable_login_with_phone      = true
  default_redirect_uri          = local.admin_url
  password_check_lifetime       = "240h0m0s"
  external_login_check_lifetime = "240h0m0s"
  mfa_init_skip_lifetime        = "0s"
  second_factor_check_lifetime  = "24h0m0s"
  multi_factor_check_lifetime   = "24h0m0s"
}

module "zitadel" {
  source            = "../../modules/zitadel"
  environment       = "lokaal"
  site_url          = local.site_url
  admin_url         = local.admin_url
  admin_org_id      = zitadel_org.beheer.id
  local_development = true
}

# Testaccounts. Lokaal met wachtwoord, zodat je zonder e-mail of passkey kunt inloggen.
resource "zitadel_human_user" "beheerder" {
  org_id                       = zitadel_org.beheer.id
  user_name                    = "beheerder@kleurhoek.localhost"
  first_name                   = "Lokale"
  last_name                    = "Beheerder"
  email                        = "beheerder@kleurhoek.localhost"
  is_email_verified            = true
  initial_password             = local.password
  initial_skip_password_change = true
  preferred_language           = "nl"
}

resource "zitadel_human_user" "ouder" {
  org_id                       = module.zitadel.site_org_id
  user_name                    = "ouder@kleurhoek.localhost"
  first_name                   = "Mila"
  last_name                    = "Jansen"
  email                        = "ouder@kleurhoek.localhost"
  is_email_verified            = true
  initial_password             = local.password
  initial_skip_password_change = true
  preferred_language           = "nl"
}

resource "local_sensitive_file" "api" {
  filename        = "${var.output_dir}/api.env"
  file_permission = "0644"
  content         = <<-EOT
    OIDC_ISSUER=${local.issuer}
    OIDC_AUDIENCE=${module.zitadel.project_id}
    ADMIN_ORG_ID=${zitadel_org.beheer.id}
    SITE_ORG_ID=${module.zitadel.site_org_id}
    ADMIN_BOOTSTRAP_SUBJECTS=${zitadel_human_user.beheerder.id}
  EOT
}

resource "local_sensitive_file" "web" {
  filename        = "${var.output_dir}/web.env"
  file_permission = "0644"
  content         = <<-EOT
    OIDC_ISSUER=${local.issuer}
    OIDC_CLIENT_ID=${module.zitadel.web_client_id}
    OIDC_CLIENT_SECRET=${module.zitadel.web_client_secret}
    OIDC_PROJECT_ID=${module.zitadel.project_id}
    OIDC_ORG_ID=${module.zitadel.site_org_id}
    SITE_URL=${local.site_url}
  EOT
}

resource "local_sensitive_file" "admin" {
  filename        = "${var.output_dir}/admin.env"
  file_permission = "0644"
  content         = <<-EOT
    OIDC_ISSUER=${local.issuer}
    OIDC_CLIENT_ID=${module.zitadel.admin_client_id}
    OIDC_CLIENT_SECRET=${module.zitadel.admin_client_secret}
    OIDC_PROJECT_ID=${module.zitadel.project_id}
    ADMIN_ORG_ID=${zitadel_org.beheer.id}
    ADMIN_URL=${local.admin_url}
  EOT
}
