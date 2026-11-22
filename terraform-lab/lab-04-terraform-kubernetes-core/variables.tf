variable "namespace_name" {
  description = "Oluşturulacak Kubernetes isim alanı"
  type        = string
  default     = "terraform-core-lab"
}

variable "database_password" {
  description = "Veritabanı güvenli parolası"
  type        = string
  default     = "TfSuperSecretPassword99!"
  sensitive   = true
}
