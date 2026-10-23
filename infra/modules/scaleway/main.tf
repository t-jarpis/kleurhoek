# Kleurhoek bij Scaleway (regio Amsterdam): één project per omgeving met een privénetwerk, PostgreSQL
# zonder publieke ingang, een container registry en drie Serverless Containers (API, website, admin).
# Zero trust: de database en de API zijn alleen via het privénetwerk bereikbaar; website en admin
# weigeren verkeer dat niet via Cloudflare komt (geheime header, zie apps/web/src/proxy.ts).

terraform {
  required_providers {
    scaleway = { source = "scaleway/scaleway", version = "~> 2.88" }
    random   = { source = "hashicorp/random", version = "~> 3.7" }
  }
}

locals {
  name = "kleurhoek-${var.environment}"
  prod = var.environment == "prod"
  tags = concat(["site=kleurhoek", "environment=${var.environment}", "managed_by=terraform"], var.tags)
}

# Registry-namen zijn wereldwijd uniek per regio.
resource "random_id" "suffix" {
  byte_length = 3
}

# ---------- Netwerk ----------

resource "scaleway_vpc" "main" {
  name = local.name
  tags = local.tags
}

resource "scaleway_vpc_private_network" "main" {
  name   = local.name
  vpc_id = scaleway_vpc.main.id
  tags   = local.tags
}

# ---------- Database ----------

resource "random_password" "db" {
  length      = 40
  special     = true
  min_special = 2
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  # Tekens die in een connection string geen escape nodig hebben.
  override_special = "-_."
}

# Geen load_balancer-blok: dan heeft de database alleen een privé-endpoint.
resource "scaleway_rdb_instance" "main" {
  name                      = local.name
  node_type                 = var.database.node_type
  engine                    = var.database.engine
  is_ha_cluster             = var.database.ha
  user_name                 = "kleurhoek_admin"
  password                  = random_password.db.result
  volume_type               = "sbs_5k"
  volume_size_in_gb         = var.database.volume_gb
  encryption_at_rest        = true
  disable_backup            = false
  backup_schedule_frequency = var.database.backup_hours
  backup_schedule_retention = var.database.backup_days
  backup_same_region        = var.database.backup_same_dc
  tags                      = local.tags

  private_network {
    pn_id       = scaleway_vpc_private_network.main.id
    enable_ipam = true
  }
}

resource "scaleway_rdb_database" "kleurhoek" {
  instance_id = scaleway_rdb_instance.main.id
  name        = "kleurhoek"
}

resource "scaleway_rdb_privilege" "admin" {
  instance_id   = scaleway_rdb_instance.main.id
  user_name     = scaleway_rdb_instance.main.user_name
  database_name = scaleway_rdb_database.kleurhoek.name
  permission    = "all"
}

locals {
  db_endpoint  = scaleway_rdb_instance.main.private_network[0]
  database_url = "postgres://${scaleway_rdb_instance.main.user_name}:${random_password.db.result}@${local.db_endpoint.ip}:${local.db_endpoint.port}/${scaleway_rdb_database.kleurhoek.name}"
}

# ---------- Registry ----------

resource "scaleway_registry_namespace" "main" {
  name        = "${local.name}-${random_id.suffix.hex}"
  description = "Images van Kleurhoek (${var.environment})"
  is_public   = false
}

# ---------- Geheimen ----------
# Komen als versleutelde omgevingsvariabelen in de containers. Ze staan ook in de Terraform-state;
# die staat daarom in een privé bucket met versleuteling en alleen jouw sleutel.

resource "random_password" "secret" {
  for_each = toset(["ingest-key", "analytics-salt", "web-session-secret", "admin-session-secret", "login-secret"])
  length   = 48
  special  = false
}

# ---------- Uitrollen vanuit GitHub ----------
# Scaleway kent (nog) geen inloggen via OIDC vanuit GitHub. Daarom een eigen applicatie die alleen
# images mag pushen en containers mag bijwerken, binnen dit project. De sleutel gaat als geheim naar
# de GitHub-omgeving.

data "scaleway_account_project" "current" {}

resource "scaleway_iam_application" "deploy" {
  name        = "${local.name}-github-deploy"
  description = "Uitrollen vanuit GitHub Actions (t-jarpis/kleurhoek, omgeving ${var.environment})"
}

resource "scaleway_iam_policy" "deploy" {
  name           = "${local.name}-github-deploy"
  application_id = scaleway_iam_application.deploy.id
  rule {
    project_ids          = [data.scaleway_account_project.current.id]
    permission_set_names = ["ContainerRegistryFullAccess", "ContainersFullAccess"]
  }
}

resource "scaleway_iam_api_key" "deploy" {
  application_id     = scaleway_iam_application.deploy.id
  description        = "GitHub Actions (${var.environment})"
  default_project_id = data.scaleway_account_project.current.id
  # De provider ziet hier steeds een verschil en zou de sleutel elke keer vervangen.
  # Roteren gaat bewust met: terraform apply -replace=…scaleway_iam_api_key.deploy
  lifecycle {
    ignore_changes = [default_project_id, description, expires_at]
  }
}

# ---------- Logs lezen vanuit GitHub (workflow Diagnose) ----------
# Scaleway bewaart de uitvoer van de containers in Cockpit. Met dit token (alleen lezen) kan de
# Diagnose-workflow de logs ophalen, zodat fouten zonder de console te vinden zijn.

data "scaleway_cockpit_source" "logs" {
  project_id = data.scaleway_account_project.current.id
  type       = "logs"
  origin     = "scaleway"
}

resource "scaleway_cockpit_token" "diagnose" {
  project_id = data.scaleway_account_project.current.id
  name       = "${local.name}-github-diagnose"
  scopes {
    query_logs    = true
    write_logs    = false
    query_metrics = false
    write_metrics = false
  }
}
