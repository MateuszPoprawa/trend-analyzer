resource "azurerm_cognitive_account" "language" {
  name                = "ai-summary-generator"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  kind     = "TextAnalytics"
  sku_name = "S"
}