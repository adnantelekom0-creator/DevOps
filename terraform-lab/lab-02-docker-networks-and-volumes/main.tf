# 1. Özel Docker Ağı (Bridge Network)
resource "docker_network" "custom_net" {
  name   = var.network_name
  driver = "bridge"
}

# 2. Kalıcı Docker Diski (Volume)
resource "docker_volume" "redis_data" {
  name = var.redis_volume_name
}

# 3. İmajlar
resource "docker_image" "redis" {
  name         = "redis:7-alpine"
  keep_locally = true
}

resource "docker_image" "webapp" {
  name         = "hashicorp/http-echo:latest"
  keep_locally = true
}

# 4. Redis Konteyneri (Ağa bağlı ve Volume bağlı)
resource "docker_container" "redis_db" {
  name  = "backend-cache-db"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.custom_net.name
  }

  volumes {
    volume_name    = docker_volume.redis_data.name
    container_path = "/data"
  }

  restart = "unless-stopped"
}

# 5. Web Uygulama Konteyneri (Aynı ağda)
resource "docker_container" "web" {
  name  = "frontend-api"
  image = docker_image.webapp.image_id

  command = ["-text=Özel Docker Ağında Çalışıyor", "-listen=:8080"]

  networks_advanced {
    name = docker_network.custom_net.name
  }

  ports {
    internal = 8080
    external = 8080
  }

  # Sunucudaki Nginx <sunucu-adı>-kibana.devopsatolyesi.com adresini 127.0.0.1:15601'e yönlendirir
  ports {
    internal = 8080
    external = 15601
  }

  restart = "unless-stopped"
}
