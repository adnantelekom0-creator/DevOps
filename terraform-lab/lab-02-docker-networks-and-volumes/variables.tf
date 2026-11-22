variable "network_name" {
  description = "Docker özel ağının adı"
  type        = string
  default     = "lab-bridge-network"
}

variable "redis_volume_name" {
  description = "Redis kalıcı veri diskinin adı"
  type        = string
  default     = "redis-persistent-data"
}
