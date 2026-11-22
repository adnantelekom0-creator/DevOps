# 00 — Jenkins Mimarisi, Temel Kavramlar ve CI/CD Teori Rehberi

Bu doküman, modern sürekli entegrasyon ve sürekli dağıtım (CI/CD) süreçlerinde Jenkins otomasyon sunucusunun rolünü, mimari bileşenlerini, ekosistem araçlarıyla karşılaştırmasını ve laboratuvar altyapı sözlüğünü kapsamlı bir mühendislik bakışıyla açıklar.

---

## 1. Jenkins Nedir ve Neden Tercih Edilir?

**Jenkins**, Java tabanlı (LTS JDK 21), açık kaynaklı ve dağıtık mimariyi destekleyen endüstri standardı bir otomasyon sunucusudur. Sürekli Entegrasyon (CI) ve Sürekli Dağıtım (CD) süreçlerinde kaynak kod yönetiminden (SCM) başlayarak derleme, test, statik analiz, imaj paketleme ve hedef ortamlara (Bare-Metal, Sanal Makine, Kubernetes) dağıtım adımlarını otomatikleştirir.

### Temel Tercih Nedenleri:
1. **Altyapı Bağımsızlığı:** Kendi veri merkezinizde, hava boşluklu (air-gapped) izole ağlarda, yerel sanal makinelerde veya herhangi bir genel bulut sağlayıcıda (Azure, AWS, GCP) tam kontrol ve veri egemenliğiyle çalışır.
2. **Geniş Eklenti Ekosistemi:** 1.800'den fazla topluluk ve kurumsal eklenti (Plugin) sayesinde Git sunucularından derleyicilere, güvenlik tarayıcılarından bulut orkestratörlerine kadar tüm araç zinciriyle entegre olur.
3. **Maliyet Etkinliği:** Açık kaynaklıdır; lisanslama maliyeti bulunmaz. İşletim maliyeti tamamen tahsis edilen altyapı optimizasyonuna bağlıdır.
4. **Pipeline as Code Desteği:** Süreçlerin tamamı versiyon kontrol sisteminde saklanan ve denetlenebilen `Jenkinsfile` (Groovy DSL) dosyaları ile kod olarak yönetilir.

---

## 2. CI/CD Araçları Karşılaştırması

Modern DevOps ekosisteminde yaygın olarak kullanılan üç büyük CI/CD motorunun kurumsal karşılaştırması:

| Kriter | Jenkins | GitLab CI/CD | GitHub Actions |
|---|---|---|---|
| **Barındırma Modeli** | Self-hosted (Varsayılan ve Tam Kontrol) | SaaS veya Self-hosted (Omnibus / K8s) | SaaS veya Self-hosted Runner |
| **Pipeline Tanım Formatı** | Groovy DSL (Declarative / Scripted) | YAML (`.gitlab-ci.yml`) | YAML (`.github/workflows/*.yml`) |
| **SCM Bağımlılığı** | **Bağımsız** (GitLab, GitHub, Bitbucket, SVN, vb.) | GitLab odaklı ve yerleşik | GitHub odaklı ve yerleşik |
| **Yönetim Yükü** | Yüksek (Controller, plugin, JVM, disk ve ağ bakımı) | Orta (Runner yönetimi ve kayıt tokenları) | Düşük (SaaS) / Orta (Self-hosted Runner) |
| **Özelleştirme Yeteneği** | **Çok Yüksek** (Shared Library, Java API, Dahili Script Console) | Yüksek (`include`, CI/CD Components) | Yüksek (Composite Actions, Marketplace) |
| **Ekosistem Uyumu** | Karmaşık legacy ve cloud-native hibrit yapılar | GitLab tek platform (DevSecOps) yaklaşımı | GitHub geliştirici odaklı ekosistem |

---

## 3. Jenkins Mimarisi: Controller ve Agent (Node)

Jenkins, tek merkezden yönetilen fakat job'ları dağıtık node'lara delege eden iki katmanlı bir yürütme mimarisi kullanır:

```text
                      ┌─────────────────────────────────────────┐
                      │           Jenkins Controller            │
                      │  - Web UI (Port 18080 / 8080)           │
                      │  - Job Kuyruğu (Queue) & Scheduler      │
                      │  - Webhook Karşılama & Olay Yönetimi    │
                      │  - Pipeline Script Motoru (Groovy JVM)  │
                      └────────────────────┬────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │ (SSH / Inbound JNLP)                        │ (Docker Socket / K8s API)
                    ▼                                             ▼
       ┌──────────────────────────┐                  ┌──────────────────────────┐
       │   Static Agent (VM/Node) │                  │   Dynamic Pod / Docker   │
       │  - Remoting (agent.jar)  │                  │  - İhtiyaç anında kalkar │
       │  - Sabit Workspace       │                  │  - Job bittiğinde silinir│
       │  - Ortam araçları yüklü  │                  │  - İzolasyon garantisi   │
       └──────────────────────────┘                  └──────────────────────────┘
```

### Controller (Eski adıyla Master):
- Web arayüzünü (GUI) sunar, kullanıcı oturumlarını ve yetkilendirmeyi (RBAC) yönetir.
- Kaynak kod repository'lerinden gelen Webhook bildirimlerini karşılar.
- `Jenkinsfile` betiklerini derleyip mantıksal aşamalara böler ve uygun etiketli (`label`) ajanlara iletir.
- **Üretim Standardı:** Controller üzerinde derleme, test veya konteyner build işlemleri doğrudan çalıştırılmamalıdır. Controller executor sayısı `0` olarak ayarlanmalı; tüm iş yükü ajanlara veya izole konteynerlere devredilmelidir.

### Agent (Node / Worker):
- Controller'dan aldığı atomik adımları (`sh`, `bat`, `checkout`, `docker`) işleten yürütme ortamıdır.
- Üzerinde `agent.jar` (Remoting) çalışır.
- Controller ile iki ana protokolle haberleşir:
  1. **SSH:** Controller ajana SSH üzerinden bağlanır ve ajanı başlatır (Statik VM/Linux ajanlar için uygundur).
  2. **Inbound (JNLP / TCP Port 50000):** Ajan Controller'a giden bağlantı açarak iş talebinde bulunur (Güvenlik duvarı arkasındaki veya dinamik kalkan konteyner ajanlar için uygundur).
- **Dynamic Pod / Konteyner Agent:** Job başladığında Kubernetes (KinD) üzerinde pod veya host üzerinde Docker konteyneri olarak ayağa kalkan, işlem bittiğinde tamamen yok olan ve kaynak tüketmeyen modern ajan modelidir.

---

## 4. Temel Kavramlar Sözlüğü

| Terim | Tanım ve Mühendislik Karşılığı |
|---|---|
| **Freestyle Job** | Adımların ve seçeneklerin Jenkins web arayüzündeki grafik kutucuklar üzerinden tıkla-seç yöntemiyle tanımlandığı eski modeldir. Versiyon kontrol sisteminde saklanamaz; ekip içi kod incelemesine (Code Review) kapalıdır. |
| **Pipeline Job** | Tüm derleme ve dağıtım sürecinin `Jenkinsfile` adında bir metin dosyasında kod olarak tanımlandığı modern standarttır (Pipeline as Code). SCM üzerinde commit'lenir, dallara göre sürümlenir. |
| **Node / Agent** | Job'ların fiilen üzerinde koşturulduğu fiziksel, sanal veya konteyner tabanlı yürütme makinesidir. |
| **Stage** | Pipeline'ın mantıksal ve kronolojik bölümleridir (örn: `"Birim Test"`, `"SonarQube SAST"`, `"Docker Build"`, `"K8s Deploy"`). Jenkins arayüzünde görsel Stage View olarak izlenir. |
| **Step** | Bir `stage` içerisinde koşturulan en küçük atomik komuttur (`sh`, `echo`, `checkout`, `archiveArtifacts`, `withCredentials`). |
| **Groovy DSL** | Jenkins Pipeline motorunun arkasında çalışan, Java Virtual Machine (JVM) tabanlı, nesne yönelimli dinamik betik dilidir. |
| **Scripted Pipeline** | Tamamen saf Groovy kodu ile yazılan, `node { ... }` bloğuyla başlayan, katı şablonu olmayan, programatik fakat okunabilirliği ve hata yakalaması daha zor olan pipeline türüdür. |
| **Declarative Pipeline** | `pipeline { agent ... stages ... }` yapısıyla başlayan, yapılandırılmış, okunabilirliği yüksek, endüstri standardı modern deklaratif sözdizimidir. |
| **`script { ... }` Bloğu** | Declarative Pipeline içerisinde döngüler (`for-in`, `.each`), mantıksal dallanmalar (`if-else`) veya istisna yönetimi (`try-catch`) gibi saf Groovy kodlarını güvenle çalıştırmak için açılan kaçış bloğudur. |
| **Shared Library** | Pipeline'larda kod tekrarını önlemek amacıyla ortak Groovy fonksiyonlarının (`vars/`) merkezi bir Git repository'sinde tutularak `@Library` direktifiyle projelerde tek satırda çağrılmasıdır. |
| **Workspace** | Controller veya ajan üzerinde her proje için ayrılan, kaynak kodların çekildiği ve geçici derleme çıktılarının üretildiği çalışma dizinidir (`/var/jenkins_home/workspace/<job-adi>`). |

---

## 5. Platform Mimarisi ve Laboratuvar Ortamı

Laboratuvarlarımız, tek bir Azure Ubuntu 24.04 sanal makinesi üzerinde host Docker soketi aracılığıyla birbiriyle haberleşen mikroservis ve platform bileşenlerinden oluşur:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Sanal Makine Host (Ubuntu 24.04 - 4 vCPU, 16 GB RAM)                        │
│                                                                             │
│  ├── Docker Daemon (/var/run/docker.sock)                                   │
│  │                                                                          │
│  ├── [Container: jenkins]         Port: 127.0.0.1:18080 (Prefix: /jenkins)  │
│  ├── [Container: gitlab]          Port: 127.0.0.1:18929 (Path: /gitlab)     │
│  ├── [Container: devops-registry] Port: 127.0.0.1:18444 (Harbor / Registry) │
│  ├── [Container: sonarqube]       Port: 127.0.0.1:19000 (Path: /sonar)      │
│  ├── [Container: argocd-server]   Port: 127.0.0.1:18082 (Path: /argocd)     │
│  │                                                                          │
│  ├── [KinD Cluster: devops-cluster]                                         │
│  │    ├── devops-cluster-control-plane (Kube API: 172.18.0.1:6443)          │
│  │    ├── devops-cluster-worker                                             │
│  │    └── devops-cluster-worker2                                            │
│  │                                                                          │
│  └── [Nginx Master Proxy]         Port: 80 / 443                            │
│       ├── Doğrudan IP Rotaları: http://<IP>/jenkins, /gitlab, /sonar        │
│       └── Wildcard Subdomain: https://studentXX-jenkins.devopsatolyesi.com  │
└─────────────────────────────────────────────────────────────────────────────┘
```

Bu laboratuvar serisinde, sıfır harici bağımlılıkla yerel servisler entegre edilecek; kod commit'inden Kubernetes canlı dağıtımına kadar tüm adımlar gerçekçi mühendislik pratikleriyle işletilecektir.
