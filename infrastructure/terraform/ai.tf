resource "azurerm_cognitive_account" "language" {
  name                = "ai-news-trends"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  
  kind     = "TextAnalytics"
  sku_name = "S"
}