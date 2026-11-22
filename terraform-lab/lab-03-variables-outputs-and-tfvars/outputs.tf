output "full_container_name" {
  value = local.container_full_name
}

output "applied_labels" {
  value = local.standard_labels
}

output "access_url" {
  value = "http://localhost:${var.app_port}"
}
