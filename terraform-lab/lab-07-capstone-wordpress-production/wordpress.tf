# 6. WordPress Deployment (2 Adet Pod ile Çalışır)
resource "kubernetes_deployment_v1" "wordpress" {
  metadata {
    name      = "wordpress"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
    labels = {
      app  = "wordpress-platform"
      role = "frontend"
    }
  }

  spec {
    replicas = var.wordpress_replicas

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_surge       = 1
        max_unavailable = 0
      }
    }

    selector {
      match_labels = {
        app  = "wordpress-platform"
        role = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          app  = "wordpress-platform"
          role = "frontend"
        }
      }

      spec {
        container {
          name  = "wordpress"
          image = "wordpress:7.0-apache"

          port {
            name           = "http"
            container_port = 80
          }

          env {
            name  = "WORDPRESS_DB_HOST"
            value = "${kubernetes_service_v1.mysql_headless.metadata[0].name}.${kubernetes_namespace_v1.wp_ns.metadata[0].name}.svc.cluster.local:3306"
          }

          env {
            name = "WORDPRESS_DB_NAME"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_DATABASE"
              }
            }
          }

          env {
            name = "WORDPRESS_DB_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_USER"
              }
            }
          }

          env {
            name = "WORDPRESS_DB_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_PASSWORD"
              }
            }
          }

          # Ortak medya/yüklemeler diski (Her 2 pod da bu dizini paylaşır)
          volume_mount {
            name       = "shared-uploads"
            mount_path = "/var/www/html/wp-content/uploads"
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "300m"
              memory = "512Mi"
            }
          }

          readiness_probe {
            http_get {
              path = "/wp-admin/install.php"
              port = 80
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }

          liveness_probe {
            http_get {
              path = "/wp-admin/install.php"
              port = 80
            }
            initial_delay_seconds = 20
            period_seconds        = 10
          }
        }

        volume {
          name = "shared-uploads"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.wp_shared_storage.metadata[0].name
          }
        }
      }
    }
  }

  depends_on = [kubernetes_stateful_set_v1.mysql]
}

# 7. WordPress Servisi (ClusterIP)
resource "kubernetes_service_v1" "wordpress_service" {
  metadata {
    name      = "wordpress-service"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
    labels = {
      app  = "wordpress-platform"
      role = "frontend"
    }
  }

  spec {
    selector = {
      app  = "wordpress-platform"
      role = "frontend"
    }

    port {
      name        = "http"
      port        = 80
      target_port = 80
    }

    type = "ClusterIP"
  }
}
