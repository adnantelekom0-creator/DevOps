# 3. WordPress Paylaşılan Depolama (Shared Volume Claim - uploads/medya)
# Her iki WordPress podunun ortak medya klasörüne erişebilmesi için PVC tanımlanır
resource "kubernetes_persistent_volume_claim_v1" "wp_shared_storage" {
  metadata {
    name      = "wordpress-shared-pvc"
    namespace = kubernetes_namespace_v1.wp_ns.metadata[0].name
  }

  wait_until_bound = false

  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}
