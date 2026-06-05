output "service_bus_connection_string" {
  value     = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string
  sensitive = true
}

output "cosmos_endpoint" {
  value = azurerm_cosmosdb_account.cosmos.endpoint
}

output "ai_endpoint" {
  value = azurerm_cognitive_account.language.endpoint
}

output "query_function_name" {
  value = azurerm_linux_function_app.query.name
}

output "nlp_function_name" {
  value = azurerm_linux_function_app.nlp.name
}

output "trend_function_name" {
  value = azurerm_linux_function_app.trend.name
}

output "frontend_url" {
  value = azurerm_container_app.frontend.ingress[0].fqdn
}