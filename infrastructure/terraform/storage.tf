resource "azurerm_storage_account" "storage" {
  name                     = "stnewstrends12345"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  account_tier             = "Standard"
  account_replication_type = "LRS"
}