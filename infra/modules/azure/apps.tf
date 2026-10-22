# Container Apps: API, website en admin panel, plus jobs voor migraties en de seed.
# De deploy-workflow zet nieuwe images; Terraform beheert de rest en laat het image met rust.

resource "azurerm_container_app_environment" "main" {
  name                           = "cae-${local.name}"
  location                       = azurerm_resource_group.main.location
  resource_group_name            = azurerm_resource_group.main.name
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id       = azurerm_subnet.apps.id
  internal_load_balancer_enabled = false
  zone_redundancy_enabled        = local.prod
  # Verkeer tussen de apps onderling versleuteld (peer-to-peer).
  mutual_tls_enabled = true
  tags               = local.tags

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}

locals {
  # Website en admin: alleen verkeer van Cloudflare. De API heeft geen publieke ingang: alleen
  # website en admin roepen hem aan, binnen de omgeving. SVG's gaan via de website (en het CDN).
  ingress_allow = var.allowed_ingress_cidrs

  kv_ref = { for k, s in azurerm_key_vault_secret.main : k => s.versionless_id }

  apps = {
    api = {
      port         = 3001
      cpu          = 0.5
      memory       = "1Gi"
      min          = var.replicas.api_min
      max          = var.replicas.api_max
      health       = "/health"
      public       = false
      host         = null
      secret_names = ["database-url", "ingest-key"]
      env = {
        NODE_ENV                 = "production"
        PORT                     = "3001"
        TENANT_ID                = var.tenant_id
        OIDC_ISSUER              = var.oidc.issuer
        OIDC_AUDIENCE            = var.oidc.project_id
        ADMIN_ORG_ID             = var.oidc.admin_org_id
        SITE_ORG_ID              = var.oidc.site_org_id
        ADMIN_BOOTSTRAP_SUBJECTS = join(",", var.admin_bootstrap_subjects)
      }
      secret_env = { DATABASE_URL = "database-url", INGEST_KEY = "ingest-key" }
    }
    web = {
      port         = 3000
      cpu          = 0.5
      memory       = "1Gi"
      min          = var.replicas.web_min
      max          = var.replicas.web_max
      health       = "/healthz"
      public       = true
      host         = var.hosts.site
      secret_names = ["ingest-key", "analytics-salt", "web-session-secret", "web-oidc-secret"]
      env = {
        NODE_ENV            = "production"
        API_URL             = "http://ca-${local.name}-api"
        NEXT_PUBLIC_MARKETS = var.markets
        SITE_URL            = "https://${var.hosts.site}"
        OIDC_ISSUER         = var.oidc.issuer
        OIDC_CLIENT_ID      = var.oidc.web_client_id
        OIDC_PROJECT_ID     = var.oidc.project_id
        OIDC_ORG_ID         = var.oidc.site_org_id
      }
      secret_env = { INGEST_KEY = "ingest-key", ANALYTICS_SALT_SECRET = "analytics-salt", SESSION_SECRET = "web-session-secret", OIDC_CLIENT_SECRET = "web-oidc-secret" }
    }
    admin = {
      port         = 3002
      cpu          = 0.25
      memory       = "0.5Gi"
      min          = 0
      max          = 1
      health       = "/healthz"
      public       = true
      host         = var.hosts.admin
      secret_names = ["admin-session-secret", "admin-oidc-secret"]
      env = {
        NODE_ENV        = "production"
        API_URL         = "http://ca-${local.name}-api"
        ADMIN_URL       = "https://${var.hosts.admin}"
        OIDC_ISSUER     = var.oidc.issuer
        OIDC_CLIENT_ID  = var.oidc.admin_client_id
        OIDC_PROJECT_ID = var.oidc.project_id
        ADMIN_ORG_ID    = var.oidc.admin_org_id
      }
      secret_env = { SESSION_SECRET = "admin-session-secret", OIDC_CLIENT_SECRET = "admin-oidc-secret" }
    }
  }
}

resource "azurerm_container_app" "app" {
  for_each                     = local.apps
  name                         = "ca-${local.name}-${each.key}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"
  tags                         = local.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.app[each.key].id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.app[each.key].id
  }

  dynamic "secret" {
    for_each = toset(each.value.secret_names)
    content {
      name                = secret.value
      key_vault_secret_id = local.kv_ref[secret.value]
      identity            = azurerm_user_assigned_identity.app[each.key].id
    }
  }

  ingress {
    external_enabled = each.value.public
    target_port      = each.value.port
    transport        = "auto"
    # Intern (API) via http://<naam> binnen de omgeving, versleuteld door mutual TLS van de omgeving.
    allow_insecure_connections = !each.value.public
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
    dynamic "ip_security_restriction" {
      for_each = each.value.public ? { for i, cidr in local.ingress_allow : i => cidr } : {}
      content {
        name             = "allow-${ip_security_restriction.key}"
        action           = "Allow"
        ip_address_range = ip_security_restriction.value
      }
    }
  }

  template {
    min_replicas                     = each.value.min
    max_replicas                     = each.value.max
    termination_grace_period_seconds = 30

    container {
      name   = each.key
      image  = var.bootstrap_image
      cpu    = each.value.cpu
      memory = each.value.memory

      dynamic "env" {
        for_each = each.value.env
        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = each.value.secret_env
        content {
          name        = env.key
          secret_name = env.value
        }
      }

      startup_probe {
        transport               = "HTTP"
        port                    = each.value.port
        path                    = each.value.health
        interval_seconds        = 5
        failure_count_threshold = 24
      }
      liveness_probe {
        transport        = "HTTP"
        port             = each.value.port
        path             = each.value.health
        interval_seconds = 30
      }
      readiness_probe {
        transport        = "HTTP"
        port             = each.value.port
        path             = each.value.health
        interval_seconds = 10
      }
    }

    http_scale_rule {
      name                = "http"
      concurrent_requests = "50"
    }
  }

  lifecycle {
    # Het image zet de deploy-workflow (az containerapp update), niet Terraform.
    ignore_changes = [template[0].container[0].image]
  }

  depends_on = [azurerm_role_assignment.acr_pull, azurerm_role_assignment.kv_reader]
}

# Migraties en seed: dezelfde API-image, handmatig gestart door de deploy-workflow.
resource "azurerm_container_app_job" "task" {
  for_each = {
    migrate = ["node", "dist/db/migrate.js"]
    seed    = ["node", "dist/db/seed-cli.js"]
  }
  name                         = "caj-${local.name}-${each.key}"
  location                     = azurerm_resource_group.main.location
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  workload_profile_name        = "Consumption"
  replica_timeout_in_seconds   = 600
  replica_retry_limit          = 0
  tags                         = local.tags

  manual_trigger_config {
    parallelism              = 1
    replica_completion_count = 1
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.app["api"].id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.app["api"].id
  }

  secret {
    name                = "database-url"
    key_vault_secret_id = local.kv_ref["database-url"]
    identity            = azurerm_user_assigned_identity.app["api"].id
  }

  template {
    container {
      name    = each.key
      image   = var.bootstrap_image
      command = each.value
      cpu     = 0.5
      memory  = "1Gi"
      env {
        name  = "NODE_ENV"
        value = "production"
      }
      env {
        name  = "TENANT_ID"
        value = var.tenant_id
      }
      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
      # De API-config eist deze waarden in productie, ook al gebruiken jobs ze niet.
      env {
        name  = "OIDC_ISSUER"
        value = var.oidc.issuer
      }
      env {
        name  = "OIDC_AUDIENCE"
        value = var.oidc.project_id
      }
      env {
        name  = "ADMIN_ORG_ID"
        value = var.oidc.admin_org_id
      }
      env {
        name  = "SITE_ORG_ID"
        value = var.oidc.site_org_id
      }
      env {
        name  = "INGEST_KEY"
        value = "job-heeft-geen-ingest-nodig-0000000000"
      }
    }
  }

  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }

  depends_on = [azurerm_role_assignment.acr_pull, azurerm_role_assignment.kv_reader]
}

# ---------- Eigen domeinen (achter Cloudflare) ----------

resource "azurerm_container_app_environment_certificate" "origin" {
  count                        = length(var.domain_records) > 0 ? 1 : 0
  name                         = "cloudflare-origin"
  container_app_environment_id = azurerm_container_app_environment.main.id
  certificate_blob_base64      = base64encode("${var.origin_certificate.certificate_pem}${var.origin_certificate.private_key_pem}")
  certificate_password         = ""
  tags                         = local.tags
}

resource "azurerm_container_app_custom_domain" "app" {
  # De sleutel komt pas binnen als het asuid-record in Cloudflare bestaat: zo volgt de koppeling op de DNS.
  for_each                                 = var.domain_records
  name                                     = local.apps[each.key].host
  container_app_id                         = azurerm_container_app.app[each.key].id
  container_app_environment_certificate_id = azurerm_container_app_environment_certificate.origin[0].id
  certificate_binding_type                 = "SniEnabled"
}
