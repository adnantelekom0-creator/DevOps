# 1. Kubernetes İsim Alanı (Namespace)
resource "kubernetes_namespace_v1" "lab_ns" {
  metadata {
    name = var.namespace_name
    labels = {
      managed_by  = "terraform"
      environment = "sandbox"
    }
  }
}

# 2. ConfigMap
resource "kubernetes_config_map_v1" "app_config" {
  metadata {
    name      = "global-app-config"
    namespace = kubernetes_namespace_v1.lab_ns.metadata[0].name
  }

  data = {
    APP_ENV           = "production"
    MAX_CONNECTIONS   = "200"
    FEATURE_ANALYTICS = "true"
  }
}

# 3. Gizli Veri (Secret)
resource "kubernetes_secret_v1" "app_secret" {
  metadata {
    name      = "db-credentials"
    namespace = kubernetes_namespace_v1.lab_ns.metadata[0].name
  }

  data = {
    DB_USER = "db_master"
    DB_PASS = var.database_password
  }

  type = "Opaque"
}

# 4. Kaynak Sınırlandırması (ResourceQuota)
resource "kubernetes_resource_quota_v1" "ns_quota" {
  metadata {
    name      = "namespace-hard-limits"
    namespace = kubernetes_namespace_v1.lab_ns.metadata[0].name
  }

  spec {
    hard = {
      "requests.cpu"    = "1000m"
      "requests.memory" = "1Gi"
      "limits.cpu"      = "2000m"
      "limits.memory"   = "2Gi"
      "pods"            = "10"
    }
  }
}
