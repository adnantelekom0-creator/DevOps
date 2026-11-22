variable "namespace" {
  description = "WordPress ve MySQL'in dağıtılacağı isim alanı"
  type        = string
  default     = "wordpress"
}

variable "domain_name" {
  description = "WordPress Ingress erişim domain adresi"
  type        = string
  default     = "wordpress.local"
}

variable "ingress_class_name" {
  description = "Kümede çalışan Ingress Controller'ın IngressClass adı"
  type        = string
  default     = "traefik"
}

variable "wordpress_replicas" {
  description = "Çalıştırılacak WordPress Pod kopya sayısı"
  type        = number
  default     = 2
}

variable "mysql_db_name" {
  description = "Oluşturulacak MySQL veritabanı adı"
  type        = string
  default     = "wordpress_db"
}

variable "mysql_user" {
  description = "MySQL kullanıcı adı"
  type        = string
  default     = "wp_user"
}

variable "mysql_password" {
  description = "MySQL kullanıcı parolası"
  type        = string
  default     = "SecureWpPass2026!"
  sensitive   = true
}

variable "mysql_root_password" {
  description = "MySQL root yöneticisi parolası"
  type        = string
  default     = "SuperRootPassword2026!"
  sensitive   = true
}
