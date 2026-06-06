resource "azurerm_service_plan" "plan" {
  name                = "plan-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  os_type  = "Linux"
  sku_name = "Y1"
}

resource "azurerm_application_insights" "appi" {
  name                = "appi-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  application_type = "web"
}

resource "azurerm_linux_function_app" "query" {
  name                = "func-query-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  service_plan_id = azurerm_service_plan.plan.id

  site_config {}

  app_settings = {
    SERVICE_BUS_CONNECTION = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.appi.instrumentation_key
  }
}

resource "azurerm_linux_function_app" "nlp" {
  name                = "func-nlp-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  service_plan_id = azurerm_service_plan.plan.id

  site_config {}

  app_settings = {
    SERVICE_BUS_CONNECTION = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string
    AZURE_AI_ENDPOINT      = azurerm_cognitive_account.language.endpoint
    AZURE_AI_KEY           = azurerm_cognitive_account.language.primary_access_key
  }
}

resource "azurerm_linux_function_app" "trend" {
  name                = "func-trend-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  service_plan_id = azurerm_service_plan.plan.id

  site_config {}

  app_settings = {
    SERVICE_BUS_CONNECTION = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string

    COSMOS_URI = azurerm_cosmosdb_account.cosmos.endpoint
    COSMOS_KEY = azurerm_cosmosdb_account.cosmos.primary_key
  }
}