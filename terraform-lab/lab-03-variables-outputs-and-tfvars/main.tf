locals {
  container_full_name = "app-${var.environment}-web"
  standard_labels = merge(var.app_tags, {
    managed_by = "terraform"
    env        = var.environment
  })
}

resource "docker_image" "alpine_nginx" {
  name         = "nginx:1.30-alpine"
  keep_locally = true
}

resource "docker_container" "app" {
  name  = local.container_full_name
  image = docker_image.alpine_nginx.image_id

  ports {
    internal = 80
    external = var.app_port
  }

  # Sunucudaki Nginx <sunucu-adı>-kibana.devopsatolyesi.com adresini 127.0.0.1:15601'e yönlendirir
  ports {
    internal = 80
    external = 15601
  }

  env = [
    "APP_ENV=${var.environment}",
    "TEAM=${lookup(var.app_tags, "team", "unknown")}"
  ]

  dynamic "labels" {
    for_each = local.standard_labels
    content {
      label = labels.key
      value = labels.value
    }
  }

  restart = "unless-stopped"
}
