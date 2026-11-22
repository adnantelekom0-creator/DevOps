output "container_id" {
  description = "Oluşturulan konteynerin benzersiz ID'si"
  value       = docker_container.nginx_app.id
}

output "application_url" {
  description = "Uygulamanın erişim adresi"
  value       = "http://localhost:${var.host_port}"
}
