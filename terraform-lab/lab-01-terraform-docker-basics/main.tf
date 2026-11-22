# 1. Docker İmajının Çekilmesi
resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}

# 2. Docker Konteynerinin Başlatılması
resource "docker_container" "nginx_app" {
  name  = var.container_name
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = var.host_port
  }

  # Sunucudaki Nginx <sunucu-adı>-kibana.devopsatolyesi.com adresini 127.0.0.1:15601'e yönlendirir
  ports {
    internal = 80
    external = 15601
  }

  restart = "unless-stopped"
}
