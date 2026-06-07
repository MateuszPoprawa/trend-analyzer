variable "location" {
  default = "germanywestcentral"
}

variable "project_name" {
  default = "news-trends"
}

variable "news_api_key" {
  type      = string
  sensitive = true
}