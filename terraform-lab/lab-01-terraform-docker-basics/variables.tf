variable "container_name" {
  description = "Docker konteynerinin adı"
  type        = string
  default     = "devops-nginx-app"
}

variable "host_port" {
  description = "Host makinede açılacak port"
  type        = number
  default     = 8080
}
