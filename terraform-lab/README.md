# Terraform Labları

Terraform ile Docker, Kubernetes ve Helm labları. Her klasör kendi `versions.tf`, `main.tf`, `variables.tf`, `outputs.tf` dosyalarını ve `README.md` rehberini içerir.

---

## Ön Hazırlık

- Terraform 1.5+ (`terraform version`), Docker (`docker ps`).
- Kubernetes labları (04–07) k8s-labs reposundaki Kind cluster'ını (`k8s-labs`) kullanır; yeni cluster kurulmaz:

```bash
kubectl config current-context
```

Çıktı `kind-k8s-labs` olmalıdır.

Repoyu sunucuda home dizinine klonlayın:

```bash
git clone https://gitlab.com/devops-practitioner-labs/terraform-lab.git ~/terraform-lab
```

## Terraform Registry ve Dokümantasyon Rehberi

Terraform ile çalışırken provider, resource ve data source'ların en güncel kullanım örnekleri, argümanları ve versiyon blokları resmi merkezi depodan takip edilir:

**Resmi Terraform Registry:** [https://registry.terraform.io/](https://registry.terraform.io/)

### Versiyona Göre Komutlar, Provider'lar ve Örnekler Nasıl Bulunur?

1. **Registry'de Arama:**
   * [registry.terraform.io](https://registry.terraform.io/) adresine gidin.
   * Üst menüden **Browse > Providers** seçeneğine tıklayın veya arama çubuğuna provider adını yazın (örn: `docker`, `kubernetes`, `helm`, `aws`).
2. **Doğru Provider'ı ve Sürümü Seçme:**
   * Provider sayfasında sağ üst köşedeki **"Version"** açılır menüsünden çalıştığınız sürümü (örn: `kreuzwerker/docker 4.7.0`, `hashicorp/kubernetes 3.5.0` veya `hashicorp/helm 3.3.0`) seçin.
   * **Önemli:** Terraform'da argümanlar ve kaynak isimleri majör sürümlerde değişebilir. Kodunuzda hangi sürümü kilitlediyseniz (`versions.tf`), dokümantasyonda da aynı sürümü seçmelisiniz.
3. **`USE PROVIDER` Butonu (Kurulum Sözdizimi):**
   * Sağ üstteki **"USE PROVIDER"** butonuna basarak projenizin `versions.tf` dosyasına eklemeniz gereken `required_providers` bloğunu tek tıkla kopyalayabilirsiniz.
4. **Resource ve Data Source Dokümanını Okuma:**
   * Sol menüdeki **Documentation** sekmesinden ilgili kaynağı bulun (örn: `docker_container`, `kubernetes_deployment_v1`, `helm_release`).
   * **Example Usage:** Her sayfanın başında çalışmaya hazır minimal ve kapsamlı HCL blokları bulunur.
   * **Argument Reference:** Hangi alanların zorunlu (`Required`), hangilerinin isteğe bağlı (`Optional`) olduğunu ve varsayılan değerlerini gösterir.
   * **Attributes Reference:** `terraform output` veya diğer kaynaklara referans olarak aktarabileceğiniz dönen değerleri (örn: `id`, `ip_address`, `status`) listeler.

### Bu Lablarda Kullanılan Provider'lar
* **Docker Provider (`kreuzwerker/docker`):** [https://registry.terraform.io/providers/kreuzwerker/docker/4.7.0](https://registry.terraform.io/providers/kreuzwerker/docker/4.7.0)
* **Kubernetes Provider (`hashicorp/kubernetes`):** [https://registry.terraform.io/providers/hashicorp/kubernetes/3.5.0](https://registry.terraform.io/providers/hashicorp/kubernetes/3.5.0)
* **Helm Provider (`hashicorp/helm`):** [https://registry.terraform.io/providers/hashicorp/helm/3.3.0](https://registry.terraform.io/providers/hashicorp/helm/3.3.0)

## Sunucu Portları

| Port | Nereye gider | Kullanan lab |
|---|---|---|
| 15601 | `https://<sunucu-adı>-kibana.devopsatolyesi.com`; Docker labları container'ı bu porta da yayınlar, Kubernetes labları `kubectl port-forward` ile bağlar | 01, 02, 03, 05, 06, 08 |
| 8080 | Docker container; IP ile erişim `http://<sunucu-ip>:8080` | 01, 02, 03, 08 |
| 30086, 30087 | Kind NodePort 30086, 30087; IP ile erişim | 05, 06 |
| 19001 | Kind control-plane :80 (Traefik Ingress); `https://<sunucu-adı>-app1.devopsatolyesi.com` | 07 |

Lablar aynı portları kullanır; bir lab bitince Temizlik adımlarıyla kapatıp sonrakine geçin.

## Lab Kataloğu

| Lab | Konu | Port |
|---|---|---|
| [LAB-TF-01](lab-01-terraform-docker-basics/README.md) | Docker provider, image ve container | 8080, 15601 |
| [LAB-TF-02](lab-02-docker-networks-and-volumes/README.md) | Docker network, volume, iki container | 8080, 15601 |
| [LAB-TF-03](lab-03-variables-outputs-and-tfvars/README.md) | Değişkenler, validation, locals, tfvars | 8080, 15601 |
| [LAB-TF-04](lab-04-terraform-kubernetes-core/README.md) | Namespace, ConfigMap, Secret, ResourceQuota | — |
| [LAB-TF-05](lab-05-kubernetes-deployments-and-services/README.md) | Deployment, probe, NodePort Service, ölçekleme | 30086, 15601 |
| [LAB-TF-06](lab-06-terraform-helm-provider/README.md) | Helm provider ile Ingress NGINX ve Ingress kuralı | 30087, 15601 |
| [LAB-TF-07](lab-07-capstone-wordpress-production/README.md) | Bitirme: WordPress + MySQL StatefulSet + PVC + Ingress | 19001 |
| [LAB-TF-08](lab-08-novashop-docker-stack/README.md) | NovaShop Docker stack | 8080, 15601 |

Her lab bağımsızdır. LAB-TF-07 cluster'da k8s-labs I01 ile kurulan Traefik Ingress Controller'ı kullanır.
