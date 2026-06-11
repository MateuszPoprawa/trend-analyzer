resource "azurerm_servicebus_namespace" "sb" {
  name                = "sb-summary-generator"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku = "Standard"

  depends_on = [
    azurerm_resource_group.rg
  ]
}

resource "azurerm_servicebus_topic" "articles" {
  name         = "articles"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_topic" "summary-results" {
  name         = "summary-results"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_subscription" "nlp" {
  name               = "nlp-subscription"
  topic_id           = azurerm_servicebus_topic.articles.id
  max_delivery_count = 10
}

resource "azurerm_servicebus_subscription" "summary" {
  name               = "summary-subscription"
  topic_id           = azurerm_servicebus_topic.summary-results.id
  max_delivery_count = 10
}

resource "azurerm_servicebus_namespace_authorization_rule" "functions" {
  name         = "functions-policy"
  namespace_id = azurerm_servicebus_namespace.sb.id

  listen = true
  send   = true
  manage = false
}