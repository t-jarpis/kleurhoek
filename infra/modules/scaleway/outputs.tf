output "registry_endpoint" {
  value       = scaleway_registry_namespace.main.endpoint
  description = "Bijvoorbeeld rg.nl-ams.scw.cloud/kleurhoek-dev-a1b2c3"
}

output "container_namespace_id" { value = scaleway_container_namespace.main.id }

# Region-loze ID's, voor de Containers-API in de deploy-workflow.
output "container_ids" {
  value = merge(
    { for c in scaleway_container.api : "api" => split("/", c.id)[1] },
    { for k, c in scaleway_container.public : k => split("/", c.id)[1] },
  )
}

# Standaard-hostnamen van website en admin; Cloudflare verwijst ernaar (CNAME).
output "public_hosts" {
  value = { for k, c in scaleway_container.public : k => trimprefix(c.public_endpoint, "https://") }
}

output "database" {
  value = {
    id   = scaleway_rdb_instance.main.id
    host = local.db_endpoint.ip
    port = local.db_endpoint.port
  }
}

# Voor de GitHub-omgeving: SCW_ACCESS_KEY (variable) en SCW_SECRET_KEY (secret).
output "github_deploy" {
  value = {
    access_key = scaleway_iam_api_key.deploy.access_key
    secret_key = scaleway_iam_api_key.deploy.secret_key
    project_id = data.scaleway_account_project.current.id
    logs_url   = data.scaleway_cockpit_source.logs.url
    logs_token = scaleway_cockpit_token.diagnose.secret_key
  }
  sensitive = true
}
