resource "azurerm_container_registry" "acr" {
  name                = "acrnewstrends12345"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku           = "Basic"
  admin_enabled = true
}

resource "azurerm_container_app_environment" "frontend" {
  name                       = "cae-news-trends"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name

  infrastructure_subnet_id = null
}

resource "azurerm_container_app" "frontend" {
  name                         = "frontend-news-trends"
  container_app_environment_id = azurerm_container_app_environment.frontend.id
  resource_group_name          = azurerm_resource_group.rg.name

  revision_mode = "Single"

  template {
    container {
      name   = "streamlit"
      image  = "${azurerm_container_registry.acr.login_server}/streamlit:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name = "QUERY_SERVICE_URL"
        value = "https://${azurerm_linux_function_app.query.default_hostname}/api/query"
      }

      env {
        name  = "TREND_SERVICE_URL"
        value = "https://${azurerm_linux_function_app.trend.default_hostname}/api/trends"
      }
    }

    min_replicas = 1
    max_replicas = 2
  }

  ingress {
    external_enabled = true
    target_port      = 8501

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }
}