output "namespace" {
  value = kubernetes_namespace_v1.lab_ns.metadata[0].name
}

output "configmap_name" {
  value = kubernetes_config_map_v1.app_config.metadata[0].name
}

output "secret_name" {
  value = kubernetes_secret_v1.app_secret.metadata[0].name
}
