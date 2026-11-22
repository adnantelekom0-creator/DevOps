output "service_name" {
  value = kubernetes_service_v1.webapp_svc.metadata[0].name
}

output "node_port" {
  value = kubernetes_service_v1.webapp_svc.spec[0].port[0].node_port
}

output "test_command" {
  value = "curl http://localhost:${var.node_port}"
}
