resource "azurerm_service_plan" "plan" {
  name                = "plan-news-trends"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  os_type  = "Linux"
  sku_name = "Y1"
}

resource "azurerm_application_insights" "query" {
  name                = "appi-query-news-trends"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  application_type = "web"
}

resource "azurerm_application_insights" "nlp" {
  name                = "appi-nlp-news-trends"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  application_type = "web"
}

resource "azurerm_application_insights" "trend" {
  name                = "appi-trend-news-trends"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  application_type = "web"
}

resource "azurerm_linux_function_app" "query" {
  name                = "func-query-news-trends"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  service_plan_id = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    SERVICE_BUS_CONNECTION = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.query.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
    FUNCTIONS_EXTENSION_VERSION = "~4"
    NEWS_API_KEY = var.news_api_key
  }
}

resource "azurerm_linux_function_app" "nlp" {
  name                = "func-nlp-news-trends"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  service_plan_id = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    SERVICE_BUS_CONNECTION = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.nlp.instrumentation_key
    AZURE_AI_ENDPOINT      = azurerm_cognitive_account.language.endpoint
    AZURE_AI_KEY           = azurerm_cognitive_account.language.primary_access_key
    FUNCTIONS_WORKER_RUNTIME = "python"
    FUNCTIONS_EXTENSION_VERSION = "~4"
  }
}

resource "azurerm_linux_function_app" "trend" {
  name                = "func-trend-news-trends"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  service_plan_id = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    SERVICE_BUS_CONNECTION = azurerm_servicebus_namespace_authorization_rule.functions.primary_connection_string
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.trend.instrumentation_key
    FUNCTIONS_WORKER_RUNTIME = "python"
    FUNCTIONS_EXTENSION_VERSION = "~4"
    COSMOS_URI = azurerm_cosmosdb_account.cosmos.endpoint
    COSMOS_KEY = azurerm_cosmosdb_account.cosmos.primary_key
  }
}