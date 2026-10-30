# Drie Serverless Containers in één namespace, alle drie aan het privénetwerk.
# - api: alleen een privé-endpoint (geen publieke ingang). Draait bij het opstarten de migraties
#   (en in dev de seed), met een advisory lock zodat parallelle instances op elkaar wachten.
# - web en admin: publiek, maar alleen via Cloudflare (eigen domein + geheime header).
# Images: GitHub zet nieuwe versies (tag = commit) via de Containers-API; Terraform kijkt daar niet naar.

resource "scaleway_container_namespace" "main" {
  name        = local.name
  description = "Kleurhoek (${var.environment})"
  tags        = local.tags
}

locals {
  registry = scaleway_registry_namespace.main.endpoint

  apps = {
    api = {
      port    = 3001
      cpu     = 560
      memory  = 1024
      min     = var.scale.api_min
      max     = var.scale.api_max
      health  = "/health"
      public  = false
      timeout = 300
      env = merge({
        NODE_ENV                 = "production"
        TENANT_ID                = var.tenant_id
        OIDC_ISSUER              = var.oidc.issuer
        OIDC_AUDIENCE            = var.oidc.project_id
        ADMIN_ORG_ID             = var.oidc.admin_org_id
        SITE_ORG_ID              = var.oidc.site_org_id
        ADMIN_BOOTSTRAP_SUBJECTS = join(",", var.admin_bootstrap_subjects)
        MIGRATE_ON_START         = "true"
        # De seed is aanvullend (overschrijft niets uit het admin panel): ook in prod bij elke start.
        SEED_ON_START    = "true"
        DATABASE_CA      = scaleway_rdb_instance.main.certificate
        ORG_HOST_PATTERN = var.org_host_pattern
        # Mail (ADR 0037): links in mails gaan naar de website.
        SITE_URL  = "https://${var.hosts.site}"
        MAIL_FROM = nonsensitive(var.mail.from)
        # Social (ADR 0063): terugkeeradressen na het koppelen van kanalen beginnen hiermee.
        ADMIN_URL = "https://${var.hosts.admin}"
        },
        # Zoekcijfers (ADR 0041): alleen in productie.
        length(var.search_domains) > 0 ? { SEARCH_DOMAINS = join(",", var.search_domains) } : {},
      )
      secret_env = merge({
        DATABASE_URL  = local.database_url
        INGEST_KEY    = random_password.secret["ingest-key"].result
        MAIL_SECRET   = random_password.secret["mail-secret"].result
        SOCIAL_SECRET = random_password.secret["social-secret"].result
        },
        var.social.pinterest_app_id != "" ? { PINTEREST_APP_ID = var.social.pinterest_app_id, PINTEREST_APP_SECRET = var.social.pinterest_app_secret } : {},
        var.social.meta_app_id != "" ? { META_APP_ID = var.social.meta_app_id, META_APP_SECRET = var.social.meta_app_secret } : {},
        var.mail.smtp_url != "" ? { MAIL_SMTP_URL = var.mail.smtp_url } : {},
        var.mail.transactional_smtp_url != "" ? { MAIL_TRANSACTIONAL_SMTP_URL = var.mail.transactional_smtp_url } : {},
        var.search.google_key != "" ? { GOOGLE_SEARCH_KEY = var.search.google_key } : {},
        var.search.bing_key != "" ? { BING_WEBMASTER_KEY = var.search.bing_key } : {},
      )
    }
    web = {
      port    = 3000
      cpu     = 560
      memory  = 1024
      min     = var.scale.web_min
      max     = var.scale.web_max
      health  = "/healthz"
      public  = true
      timeout = 60
      env = merge({
        NODE_ENV = "production"
        # Live markten staan in de code (ADR 0044, 0049); MARKETS_ONLY alleen voor een bewuste uitzondering.
        MARKETS_ONLY    = var.markets_only
        SITE_URL        = "https://${var.hosts.site}"
        OIDC_ISSUER     = var.oidc.issuer
        OIDC_CLIENT_ID  = var.oidc.web_client_id
        OIDC_PROJECT_ID = var.oidc.project_id
        OIDC_ORG_ID     = var.oidc.site_org_id
        },
        var.site_domains != "" ? { SITE_DOMAINS = var.site_domains } : {},
      )
      secret_env = {
        INGEST_KEY            = random_password.secret["ingest-key"].result
        ANALYTICS_SALT_SECRET = random_password.secret["analytics-salt"].result
        SESSION_SECRET        = random_password.secret["web-session-secret"].result
        SITE_CHECK_KEY        = random_password.secret["site-check-key"].result
        OIDC_CLIENT_SECRET    = var.oidc_client_secrets.web
        EDGE_SECRET           = var.edge_secret
        ORG_WORKER_SECRET     = var.org_worker_secret
      }
    }
    admin = {
      port    = 3002
      cpu     = 280
      memory  = 512
      min     = 0
      max     = 1
      health  = "/healthz"
      public  = true
      timeout = 60
      env = {
        NODE_ENV        = "production"
        ADMIN_URL       = "https://${var.hosts.admin}"
        OIDC_ISSUER     = var.oidc.issuer
        OIDC_CLIENT_ID  = var.oidc.admin_client_id
        OIDC_PROJECT_ID = var.oidc.project_id
        ADMIN_ORG_ID    = var.oidc.admin_org_id
      }
      secret_env = {
        SESSION_SECRET     = random_password.secret["admin-session-secret"].result
        OIDC_CLIENT_SECRET = var.oidc_client_secrets.admin
        EDGE_SECRET        = var.edge_secret
      }
    }
    # Eigen inlogpagina (ADR 0018): praat met Zitadel (sessies, gebruikers) en de API (huisstijl).
    login = {
      port    = 3003
      cpu     = 280
      memory  = 512
      min     = 0
      max     = 2
      health  = "/healthz"
      public  = true
      timeout = 60
      env = {
        NODE_ENV       = "production"
        ZITADEL_URL    = var.oidc.issuer
        SITE_ORG_ID    = var.oidc.site_org_id
        PASSKEY_DOMAIN = var.passkey_domain
      }
      secret_env = {
        LOGIN_SECRET        = random_password.secret["login-secret"].result
        ZITADEL_LOGIN_TOKEN = var.zitadel_login_token
        INGEST_KEY          = random_password.secret["ingest-key"].result
        EDGE_SECRET         = var.edge_secret
      }
    }
  }
}

resource "scaleway_container" "api" {
  count                          = var.apps_enabled ? 1 : 0
  name                           = "api"
  namespace_id                   = scaleway_container_namespace.main.id
  description                    = "Kleurhoek API (alleen privé-endpoint)"
  image                          = "${local.registry}/kleurhoek-api:latest"
  port                           = local.apps.api.port
  cpu_limit                      = local.apps.api.cpu
  memory_limit_bytes             = local.apps.api.memory * 1024 * 1024
  min_scale                      = local.apps.api.min
  max_scale                      = local.apps.api.max
  timeout                        = local.apps.api.timeout
  privacy                        = "public" # alleen bereikbaar via het privénetwerk, zie hieronder
  protocol                       = "http1"
  private_network_id             = scaleway_vpc_private_network.main.id
  enable_private_endpoint        = true
  enable_default_public_endpoint = false
  environment_variables          = local.apps.api.env
  secret_environment_variables   = local.apps.api.secret_env
  tags                           = local.tags

  startup_probe {
    http { path = local.apps.api.health }
    failure_threshold = 30
    interval          = "10s"
    timeout           = "5s"
  }
  liveness_probe {
    http { path = local.apps.api.health }
    failure_threshold = 3
    interval          = "30s"
    timeout           = "5s"
  }

  lifecycle {
    ignore_changes = [image, registry_sha256]
  }

  depends_on = [scaleway_rdb_privilege.admin]
}

resource "scaleway_container" "public" {
  for_each                       = var.apps_enabled ? { for k, a in local.apps : k => a if a.public } : {}
  name                           = each.key
  namespace_id                   = scaleway_container_namespace.main.id
  description                    = "Kleurhoek ${each.key} (alleen via Cloudflare)"
  image                          = "${local.registry}/kleurhoek-${each.key}:latest"
  port                           = each.value.port
  cpu_limit                      = each.value.cpu
  memory_limit_bytes             = each.value.memory * 1024 * 1024
  min_scale                      = each.value.min
  max_scale                      = each.value.max
  timeout                        = each.value.timeout
  privacy                        = "public"
  protocol                       = "http1"
  private_network_id             = scaleway_vpc_private_network.main.id
  enable_private_endpoint        = false
  enable_default_public_endpoint = true
  environment_variables          = merge(each.value.env, { API_URL = scaleway_container.api[0].private_endpoint })
  secret_environment_variables   = each.value.secret_env
  tags                           = local.tags

  startup_probe {
    http { path = each.value.health }
    failure_threshold = 30
    interval          = "10s"
    timeout           = "5s"
  }
  liveness_probe {
    http { path = each.value.health }
    failure_threshold = 3
    interval          = "30s"
    timeout           = "5s"
  }

  lifecycle {
    ignore_changes = [image, registry_sha256]
  }
}

# Eigen domein (met certificaat van Let's Encrypt via HTTP-01). Het CNAME-record in Cloudflare moet
# eerst bestaan; daarom geeft de site-module de record-ID's mee.
resource "scaleway_container_domain" "public" {
  for_each     = { for k, id in var.domain_records : k => id if contains(keys(scaleway_container.public), k) }
  container_id = scaleway_container.public[each.key].id
  hostname     = { web = var.hosts.site, admin = var.hosts.admin, login = var.hosts.login }[each.key]
}
