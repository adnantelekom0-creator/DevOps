# 4. MySQL Headless Service (Kararlı DNS İletişimi İçin)
resource "kubernetes_service_v1" "mysql_headless" {
  metadata {
    name      = "mysql-service"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
    labels = {
      app  = "wordpress-platform"
      role = "database"
    }
  }

  spec {
    cluster_ip = "None"
    selector = {
      app  = "wordpress-platform"
      role = "database"
    }

    port {
      name = "mysql"
      port = 3306
    }
  }
}

# 5. MySQL StatefulSet (Durumlu Veritabanı Kümesi)
resource "kubernetes_stateful_set_v1" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
    labels = {
      app  = "wordpress-platform"
      role = "database"
    }
  }

  spec {
    service_name = kubernetes_service_v1.mysql_headless.metadata[0].name
    replicas     = 1

    selector {
      match_labels = {
        app  = "wordpress-platform"
        role = "database"
      }
    }

    template {
      metadata {
        labels = {
          app  = "wordpress-platform"
          role = "database"
        }
      }

      spec {
        container {
          name  = "mysql"
          image = "mysql:8.4"

          port {
            name           = "mysql"
            container_port = 3306
          }

          env {
            name = "MYSQL_ROOT_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_ROOT_PASSWORD"
              }
            }
          }

          env {
            name = "MYSQL_DATABASE"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_DATABASE"
              }
            }
          }

          env {
            name = "MYSQL_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_USER"
              }
            }
          }

          env {
            name = "MYSQL_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "MYSQL_PASSWORD"
              }
            }
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }

          volume_mount {
            name       = "mysql-persistent-storage"
            mount_path = "/var/lib/mysql"
          }

          readiness_probe {
            tcp_socket {
              port = 3306
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }

          liveness_probe {
            tcp_socket {
              port = 3306
            }
            initial_delay_seconds = 20
            period_seconds        = 10
          }
        }
      }
    }

    volume_claim_template {
      metadata {
        name = "mysql-persistent-storage"
      }

      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = "1Gi"
          }
        }
      }
    }
  }
}
