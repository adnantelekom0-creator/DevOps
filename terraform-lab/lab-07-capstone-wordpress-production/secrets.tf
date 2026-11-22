# 2. Veritabanı ve WordPress Kimlik Bilgileri (Secrets)
resource "kubernetes_secret_v1" "db_credentials" {
  metadata {
    name      = "mysql-credentials"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
  }

  type = "Opaque"

  data = {
    MYSQL_DATABASE      = var.mysql_db_name
    MYSQL_USER          = var.mysql_user
    MYSQL_PASSWORD      = var.mysql_password
    MYSQL_ROOT_PASSWORD = var.mysql_root_password
  }
}
