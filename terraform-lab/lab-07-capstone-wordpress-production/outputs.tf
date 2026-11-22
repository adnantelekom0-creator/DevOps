output "wordpress_url" {
  description = "WordPress web arayüzü erişim adresi"
  value       = "https://${var.domain_name}"
}

output "mysql_internal_dns" {
  description = "MySQL veritabanının küme içi DNS adresi"
  value       = "${kubernetes_service_v1.mysql_headless.metadata[0].name}.${kubernetes_namespace_v1.wp_ns.metadata[0].name}.svc.cluster.local:3306"
}
