output "resource_group_name" { value = azurerm_resource_group.main.name }
output "acr_login_server" { value = azurerm_container_registry.main.login_server }
output "acr_name" { value = azurerm_container_registry.main.name }
output "key_vault_name" { value = azurerm_key_vault.main.name }
output "environment_verification_id" { value = azurerm_container_app_environment.main.custom_domain_verification_id }

output "app_names" {
  value = { for k, a in azurerm_container_app.app : k => a.name }
}

# Standaard-hostnamen van de publieke apps; Cloudflare verwijst ernaar (CNAME).
output "app_fqdns" {
  value = { for k, a in azurerm_container_app.app : k => a.ingress[0].fqdn if local.apps[k].public }
}

output "job_names" {
  value = { for k, j in azurerm_container_app_job.task : k => j.name }
}

# Voor de GitHub-omgeving (vars, geen geheimen): AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID.
output "github_deploy" {
  value = {
    client_id       = azurerm_user_assigned_identity.github.client_id
    tenant_id       = data.azurerm_client_config.current.tenant_id
    subscription_id = data.azurerm_client_config.current.subscription_id
  }
}
