# 1. İsim Alanı (Namespace)
resource "kubernetes_namespace_v1" "wp_ns" {
  metadata {
    name = var.namespace
    labels = {
      app        = "wordpress-platform"
      managed_by = "terraform"
      tier       = "capstone"
    }
  }
}
