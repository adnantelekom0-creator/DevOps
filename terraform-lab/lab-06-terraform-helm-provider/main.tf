# 1. Helm Release: NGINX Ingress Controller
resource "helm_release" "ingress_nginx" {
  name             = var.release_name
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  version          = "4.15.1"
  namespace        = var.namespace
  create_namespace = true

  timeout = 300
  wait    = true

  # Kind ortamına uygun controller ayarları (NodePort 30087 sunucuda 30087'ye eşlidir):
  set = [
    {
      name  = "controller.service.type"
      value = "NodePort"
    },
    {
      name  = "controller.service.nodePorts.http"
      value = "30087"
    },
    {
      name  = "controller.replicaCount"
      value = "1"
    }
  ]
}

# 2. Demo uygulama: Ingress kuralının yönlendireceği hedef
resource "kubernetes_namespace_v1" "demo" {
  metadata {
    name = var.app_namespace
  }
}

resource "kubernetes_deployment_v1" "demo" {
  metadata {
    name      = "demo-app"
    namespace = kubernetes_namespace_v1.demo.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = { app = "demo-app" }
    }

    template {
      metadata {
        labels = { app = "demo-app" }
      }

      spec {
        container {
          name  = "echo"
          image = "hashicorp/http-echo:1.0"
          args  = ["-text=LAB-TF-06: ingress-nginx -> demo-app"]

          port {
            container_port = 5678
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "demo" {
  metadata {
    name      = "demo-app"
    namespace = kubernetes_namespace_v1.demo.metadata[0].name
  }

  spec {
    selector = { app = "demo-app" }

    port {
      port        = 80
      target_port = 5678
    }
  }
}

# 3. Ingress kuralı: domain_name adresine gelen istekleri demo-app Service'ine yönlendirir
resource "kubernetes_ingress_v1" "demo" {
  metadata {
    name      = "demo-app"
    namespace = kubernetes_namespace_v1.demo.metadata[0].name
  }

  spec {
    ingress_class_name = "nginx"

    rule {
      host = var.domain_name

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service_v1.demo.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }

  # Controller ve admission webhook hazır olmadan Ingress oluşturulamaz
  depends_on = [helm_release.ingress_nginx]
}
