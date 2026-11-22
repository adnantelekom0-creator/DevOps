# 8. Kubernetes Ingress (Dış Dünyaya Erişim - Domain Yönlendirmesi)
resource "kubernetes_ingress_v1" "wordpress_ingress" {
  metadata {
    name      = "wordpress-ingress"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
  }

  spec {
    ingress_class_name = var.ingress_class_name

    rule {
      host = var.domain_name

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service_v1.wordpress_service.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
