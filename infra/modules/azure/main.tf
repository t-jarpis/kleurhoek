# Kleurhoek in Azure: één resourcegroep per omgeving met netwerk, database, registry, geheimen,
# Container Apps (API, website, admin) en jobs voor migraties en de seed.
# Zero trust: apps hebben elk een eigen managed identity, geheimen staan in Key Vault, de database is
# alleen bereikbaar via het VNet en de apps accepteren alleen verkeer van Cloudflare.

terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 5.10" }
    random  = { source = "hashicorp/random", version = "~> 3.7" }
  }
}

data "azurerm_client_config" "current" {}

locals {
  name = "kh-${var.environment}"
  # Namen zonder streepjes voor resources die dat niet toestaan; een korte hash maakt ze wereldwijd uniek.
  compact = "kh${var.environment}${substr(sha1(data.azurerm_client_config.current.subscription_id), 0, 6)}"
  tags    = merge({ site = "kleurhoek", environment = var.environment, managed_by = "terraform" }, var.tags)
  prod    = var.environment == "prod"
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${local.name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = local.prod ? 90 : 30
  tags                = local.tags
}

# ---------- Netwerk ----------

resource "azurerm_virtual_network" "main" {
  name                = "vnet-${local.name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.40.0.0/16"]
  tags                = local.tags
}

resource "azurerm_subnet" "apps" {
  name                 = "snet-apps"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.40.0.0/23"]
  delegation {
    name = "container-apps"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "postgres" {
  name                 = "snet-postgres"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.40.2.0/27"]
  delegation {
    name = "postgres"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_private_dns_zone" "postgres" {
  name                = "${local.name}.private.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                = "postgres"
  private_dns_zone_id = azurerm_private_dns_zone.postgres.id
  virtual_network_id  = azurerm_virtual_network.main.id
}

# ---------- Database ----------

resource "random_password" "postgres" {
  length  = 40
  special = false
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                          = "psql-${local.name}-${substr(local.compact, -6, 6)}"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  version                       = "17"
  sku_name                      = var.postgres.sku_name
  storage_mb                    = var.postgres.storage_mb
  auto_grow_enabled             = true
  backup_retention_days         = var.postgres.backup_days
  geo_redundant_backup_enabled  = local.prod
  delegated_subnet_id           = azurerm_subnet.postgres.id
  private_dns_zone_id           = azurerm_private_dns_zone.postgres.id
  public_network_access_enabled = false
  administrator_login           = "kleurhoek_admin"
  administrator_password        = random_password.postgres.result
  zone                          = "1"
  tags                          = local.tags

  dynamic "high_availability" {
    for_each = var.postgres.high_availability ? [1] : []
    content {
      mode                      = "ZoneRedundant"
      standby_availability_zone = "2"
    }
  }

  maintenance_window {
    day_of_week  = 0
    start_hour   = 3
    start_minute = 0
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
}

resource "azurerm_postgresql_flexible_server_database" "kleurhoek" {
  name      = "kleurhoek"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# ---------- Registry ----------

resource "azurerm_container_registry" "main" {
  name                = "acr${local.compact}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Basic"
  admin_enabled       = false
  tags                = local.tags
}

# ---------- Identiteiten ----------

resource "azurerm_user_assigned_identity" "app" {
  for_each            = toset(["api", "web", "admin"])
  name                = "id-${local.name}-${each.key}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_role_assignment" "acr_pull" {
  for_each             = azurerm_user_assigned_identity.app
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = each.value.principal_id
}

# Deploy vanuit GitHub Actions via OIDC: geen wachtwoorden of client secrets in GitHub.
resource "azurerm_user_assigned_identity" "github" {
  name                = "id-${local.name}-github"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_federated_identity_credential" "github" {
  name                      = "github-${var.environment}"
  user_assigned_identity_id = azurerm_user_assigned_identity.github.id
  issuer                    = "https://token.actions.githubusercontent.com"
  audience                  = ["api://AzureADTokenExchange"]
  subject                   = "repo:${var.github_repository}:environment:${var.environment}"
}

resource "azurerm_role_assignment" "github_acr_push" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPush"
  principal_id         = azurerm_user_assigned_identity.github.principal_id
}

# Nieuwe revisies uitrollen en jobs starten. Alleen binnen deze resourcegroep.
resource "azurerm_role_assignment" "github_deploy" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.github.principal_id
}

# ---------- Geheimen ----------

resource "azurerm_key_vault" "main" {
  name                       = "kv-${local.compact}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  purge_protection_enabled   = local.prod
  soft_delete_retention_days = local.prod ? 90 : 7
  tags                       = local.tags
}

# Wie Terraform draait, mag geheimen schrijven. De apps mogen alleen lezen.
resource "azurerm_role_assignment" "kv_officer" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "kv_reader" {
  for_each             = azurerm_user_assigned_identity.app
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = each.value.principal_id
}

resource "random_password" "secret" {
  for_each = toset(["ingest-key", "analytics-salt", "web-session-secret", "admin-session-secret"])
  length   = 48
  special  = false
}

locals {
  database_url = "postgres://kleurhoek_admin:${random_password.postgres.result}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${azurerm_postgresql_flexible_server_database.kleurhoek.name}?sslmode=require"
  secrets = {
    "database-url"         = local.database_url
    "ingest-key"           = random_password.secret["ingest-key"].result
    "analytics-salt"       = random_password.secret["analytics-salt"].result
    "web-session-secret"   = random_password.secret["web-session-secret"].result
    "admin-session-secret" = random_password.secret["admin-session-secret"].result
    "web-oidc-secret"      = var.oidc_client_secrets.web
    "admin-oidc-secret"    = var.oidc_client_secrets.admin
  }
}

resource "azurerm_key_vault_secret" "main" {
  for_each     = nonsensitive(toset(keys(local.secrets)))
  name         = each.key
  value        = local.secrets[each.key]
  key_vault_id = azurerm_key_vault.main.id
  depends_on   = [azurerm_role_assignment.kv_officer]
}
