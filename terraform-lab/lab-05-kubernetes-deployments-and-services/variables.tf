variable "app_name" {
  description = "Uygulama adı"
  type        = string
  default     = "cloud-storefront"
}

variable "replicas" {
  description = "Çalıştırılacak Pod kopya sayısı"
  type        = number
  default     = 3
}

variable "node_port" {
  description = "Dışarı açılacak NodePort numarası"
  type        = number
  default     = 30086
}
