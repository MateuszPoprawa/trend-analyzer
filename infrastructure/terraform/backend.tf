terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stnewsstate12345"
    container_name       = "tfstate"
    key                  = "news-trends.tfstate"
  }
}