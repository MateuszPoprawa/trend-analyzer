resource "azurerm_servicebus_namespace" "sb" {
  name                = "sb-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  sku = "Standard"
}

resource "azurerm_servicebus_topic" "articles" {
  name         = "articles"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_topic" "analysis" {
  name         = "analysis-results"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_subscription" "nlp" {
  name               = "nlp-subscription"
  topic_id           = azurerm_servicebus_topic.articles.id
  max_delivery_count = 10
}

resource "azurerm_servicebus_subscription" "trend" {
  name               = "trend-subscription"
  topic_id           = azurerm_servicebus_topic.analysis.id
  max_delivery_count = 10
}

resource "azurerm_servicebus_namespace_authorization_rule" "functions" {
  name         = "functions-policy"
  namespace_id = azurerm_servicebus_namespace.sb.id

  listen = true
  send   = true
  manage = false
}