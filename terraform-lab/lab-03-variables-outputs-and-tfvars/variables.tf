variable "environment" {
  description = "Dağıtım ortamı (development, staging, production)"
  type        = string
  default     = "development"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Ortam yalnızca 'development', 'staging' veya 'production' olabilir."
  }
}

variable "app_port" {
  description = "Dışarıya açılacak port numarası"
  type        = number
  default     = 8080

  validation {
    condition     = var.app_port >= 1024 && var.app_port <= 65535
    error_message = "Port numarası 1024 ile 65535 arasında olmalıdır."
  }
}

variable "app_tags" {
  description = "Uygulama etiketleri"
  type        = map(string)
  default = {
    team    = "devops"
    project = "training"
  }
}
