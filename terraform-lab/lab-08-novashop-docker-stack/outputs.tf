output "storefront_url" {
  description = "NovaShop Web Mağazası Erişim Adresi"
  value       = "http://localhost:${var.frontend_port}"
}

output "cart_db_container" {
  description = "Çalışan Sepet Veritabanı Konteyner Adı"
  value       = docker_container.cart_db.name
}

output "network_name" {
  description = "NovaShop Köprü Ağı Adı"
  value       = docker_network.novashop_net.name
}

output "cart_volume_name" {
  description = "Sepet Kalıcı Disk Adı"
  value       = docker_volume.novashop_cart_volume.name
}
