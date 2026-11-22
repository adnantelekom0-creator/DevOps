variable "docker_host" {
  description = "Docker daemon socket URI"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "environment" {
  description = "Dağıtım ortamı (dev, stage, prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Uygulama adı"
  type        = string
  default     = "novashop"
}

variable "frontend_port" {
  description = "NovaShop Frontend için dış port (IP ile erişim)"
  type        = number
  default     = 8080
}
