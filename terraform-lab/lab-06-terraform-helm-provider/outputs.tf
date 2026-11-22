output "release_status" {
  value = helm_release.ingress_nginx.status
}

output "release_version" {
  value = helm_release.ingress_nginx.version
}

output "app_url" {
  value = "https://${var.domain_name}"
}
