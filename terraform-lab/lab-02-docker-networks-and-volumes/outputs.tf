output "network_id" {
  value = docker_network.custom_net.id
}

output "web_access_url" {
  value = "http://localhost:8080"
}
