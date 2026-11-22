# 1. İzole Köprü Ağı (Bridge Network)
resource "docker_network" "novashop_net" {
  name = "${var.app_name}-${var.environment}-net"
}

# 2. Kalıcı Sepet Veri Deposu (Redis Volume)
resource "docker_volume" "novashop_cart_volume" {
  name = "${var.app_name}-cart-data"
}

# 3. İmaj Tanımları
resource "docker_image" "redis" {
  name         = "redis:7.4-alpine"
  keep_locally = true
}

resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}

# 4. Veritabanı / Cache Katmanı (NovaShop Cart DB - Redis)
resource "docker_container" "cart_db" {
  name  = "${var.app_name}-cart-redis"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.novashop_net.name
  }

  volumes {
    volume_name    = docker_volume.novashop_cart_volume.name
    container_path = "/data"
  }

  restart = "unless-stopped"
}

# 5. NovaShop Frontend / Storefront (Nginx Web)
resource "docker_container" "storefront" {
  name  = "${var.app_name}-storefront"
  image = docker_image.nginx.image_id

  networks_advanced {
    name = docker_network.novashop_net.name
  }

  ports {
    internal = 80
    external = var.frontend_port
  }

  # Sunucudaki Nginx <sunucu-adı>-kibana.devopsatolyesi.com adresini 127.0.0.1:15601'e yönlendirir
  ports {
    internal = 80
    external = 15601
  }

  upload {
    file    = "/usr/share/nginx/html/index.html"
    content = <<-EOF
      <!DOCTYPE html>
      <html>
      <head>
        <title>NovaShop E-Ticaret Platformu</title>
        <meta charset="utf-8">
        <style>
          body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 50px; }
          .card { background: #1e293b; max-width: 600px; margin: auto; padding: 30px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
          h1 { color: #38bdf8; }
          .badge { background: #10b981; color: white; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
          .info { margin-top: 20px; color: #94a3b8; font-size: 15px; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>🛍️ NovaShop Storefront</h1>
          <p><span class="badge">🚀 Terraform Docker Provider ile Ayağa Kaldırıldı</span></p>
          <div class="info">
            <p><strong>Mimari Katman:</strong> 3-Tier Docker Konteyner Mimarisi</p>
            <p><strong>Ağ Bağlantısı:</strong> novashop-dev-net (Bridge)</p>
            <p><strong>Sepet Veritabanı (Redis):</strong> novashop-cart-redis:6379</p>
            <p><strong>Port:</strong> 8080 ➔ 80</p>
          </div>
        </div>
      </body>
      </html>
    EOF
  }

  restart = "unless-stopped"
}
