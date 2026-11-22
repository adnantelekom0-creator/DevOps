# 1. Dağıtım (Deployment)
resource "kubernetes_deployment_v1" "webapp" {
  metadata {
    name = var.app_name
    labels = {
      app = var.app_name
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = var.app_name
      }
    }

    template {
      metadata {
        labels = {
          app = var.app_name
        }
      }

      spec {
        container {
          name  = "nginx-server"
          image = "nginx:1.30-alpine"

          port {
            container_port = 80
            name           = "http"
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "100m"
              memory = "128Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

# 2. Servis (NodePort)
resource "kubernetes_service_v1" "webapp_svc" {
  metadata {
    name = "${var.app_name}-service"
  }

  spec {
    selector = {
      app = var.app_name
    }

    type = "NodePort"

    port {
      port        = 80
      target_port = 80
      node_port   = var.node_port
    }
  }
}
