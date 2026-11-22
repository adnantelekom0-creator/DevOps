variable "release_name" {
  description = "Helm dağıtımının adı"
  type        = string
  default     = "nginx-ingress-controller"
}

variable "namespace" {
  description = "Helm chartının kurulacağı namespace"
  type        = string
  default     = "ingress-nginx"
}

variable "app_namespace" {
  description = "Demo uygulamanın kurulacağı namespace"
  type        = string
  default     = "ingress-demo"
}

variable "domain_name" {
  description = "Ingress kuralının yanıt vereceği alan adı"
  type        = string
  default     = "demo.local"
}
