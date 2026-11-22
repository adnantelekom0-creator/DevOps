# Jenkins CI/CD ve DevSecOps Eğitim Laboratuvarı

---

## Jenkins Teorisi ve Mimarisi

Jenkins, kurumsal yazılım geliştirme süreçlerinde sürekli entegrasyon ve sürekli teslimat (CI/CD) adımlarını otomatikleştiren açık kaynaklı bir otomasyon sunucusudur.

> Detaylı mimari dokümanı: [00-jenkins-teorisi-ve-mimarisi.md](00-jenkins-teorisi-ve-mimarisi.md)

### Temel Mimari Kavramlar:

1. **Controller / Agent Modeli:** Jenkins Controller, konfigürasyonu yönetir, işleri zamanlar ve arayüzü sunar; iş yüklerini (derleme, test, imaj derleme) ise izole çalışan Agent'lara devreder.
2. **Declarative Pipeline vs Scripted Pipeline:**
   - **Declarative Pipeline (`pipeline { ... }`):** Endüstri standardı, okunabilir, katı sözdizimli ve hata toleransı yüksek olan bildirimsel modeldir.
   - **Scripted Pipeline (`node { ... }`):** Groovy diline dayalı, programatik esnekliği yüksek fakat bakımı zor olan klasik modeldir.
3. **Jenkinsfile Temel Yapısı:**
   ```groovy
   pipeline {
       agent any
       options { timeout(time: 1, unit: 'HOURS') }
       environment { APP_ENV = 'production' }
       stages {
           stage('Build') { steps { echo 'Derleme yapılıyor...' } }
           stage('Test')  { steps { echo 'Testler koşuluyor...' } }
           stage('Deploy'){ steps { echo 'Dağıtım yapılıyor...' } }
       }
       post {
           always  { echo 'Build tamamlandı.' }
           failure { echo 'Hata oluştu!' }
       }
   }
   ```

---

## Çekirdek Laboratuvarlar (lab-01 - lab-07)

| Lab | Konu | Kullanılanlar |
|---|---|---|
| [LAB-JEN-01](lab-01-jenkins-docker-setup/README.md) | Jenkins kurulumu: arayüzle (A) ve kodla, JCasC (B) | `docker compose`, JCasC, Job DSL |
| [LAB-JEN-02](lab-02-declarative-pipeline/README.md) | Declarative Pipeline blokları, kod üreteçleri, Jenkinsfile'ı Git'ten çalıştırma | Snippet Generator, `archiveArtifacts` |
| [LAB-JEN-02A](lab-02a-python-dockerhub-kind/README.md) | Flask uygulaması: test, Docker Hub `devops-app-public` push, Kind'a deploy | Docker Hub, `kind`, `kubectl` |
| [LAB-JEN-03](lab-03-parameters-approval-resilience/README.md) | Parametreler, `when`, onay kapısı (`input`), zaman aşımı | `parameters`, `input`, `timeout` |
| [LAB-JEN-04](lab-04-credentials-docker-harbor-push/README.md) | Harbor kurulumu, credential, smoke test ve Harbor'a push | Harbor, `withCredentials` |
| [LAB-JEN-05](lab-05-sonarqube-trivy-devsecops/README.md) | SonarQube Quality Gate ve Trivy taraması | SonarQube, Trivy |
| [LAB-JEN-06](lab-06-kubernetes-kind-rolling-update/README.md) | Kind'a deploy, RollingUpdate ve otomatik rollback | `kubectl rollout` |
| [LAB-JEN-07](lab-07-devsecops-capstone-novashop/README.md) | Bitirme: test, SonarQube, Trivy, Harbor, staging, onay, production | Hepsi |

Lablar sırayla yapılır; LAB-JEN-07 önceki lablarda kurulan Harbor, SonarQube, credential'lar ve Kind cluster'ını kullanır.

---

## Bonus Laboratuvarlar (bonus-labs)

| Lab | Konu |
|---|---|
| [BONUS-JEN-01](bonus-labs/01-groovy-script-loops-conditions/README.md) | Groovy `script` blokları, döngüler, koşullar |
| [BONUS-JEN-02](bonus-labs/02-build-managers-npm-python/README.md) | Python (flake8, pytest) ve Node.js testlerini container'da çalıştırma |
| [BONUS-JEN-03](bonus-labs/03-parallel-execution-replay/README.md) | Paralel stage'ler, job tetikleme, Replay, Restart from Stage |
| [BONUS-JEN-04](bonus-labs/04-multibranch-pipeline-gitflow/README.md) | Multibranch Pipeline: dal başına otomatik job |
| [BONUS-JEN-05](bonus-labs/05-gitlab-webhook-event-driven/README.md) | GitLab webhook ile push'ta otomatik build |
| [BONUS-JEN-06](bonus-labs/06-argocd-gitops-sync/README.md) | Jenkins ve ArgoCD ile GitOps deploy |
| [BONUS-JEN-07](bonus-labs/07-shared-libraries-jcasc-ops/README.md) | Shared Library, Script Console, parola kurtarma |

---

## Port Haritası

| Servis | Port | Tarayıcı | Lab |
|---|---|---|---|
| Jenkins | `18080` | `https://<sunucu-adı>-jenkins.devopsatolyesi.com` | 01-07 |
| Harbor | `18444` | `https://<sunucu-adı>-harbor.devopsatolyesi.com` | 04, 07 |
| SonarQube | `19000` | `https://<sunucu-adı>-sonar.devopsatolyesi.com` | 05, 07 |
| Kind ingress (Traefik) | `19001` | `https://<sunucu-adı>-app1.devopsatolyesi.com` | 02A |
| Flask container (yalnız sunucudan) | `127.0.0.1:19004` | - | 02A |
| ArgoCD | `30087` | `https://SUNUCU_IP:30087` | Bonus 06 |

DNS kaydı yoksa `http://SUNUCU_IP:PORT` ile açılır; portun firewall'da açık olması gerekir.

---

## Hızlı Başlangıç

### 1. Servis Durumlarını Denetleme
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 2. Jenkins Kurulumunu Başlatma (Gerektiğinde)

Lablar LAB-JEN-01'in B bölümündeki kodla kurulan Jenkins'i kullanır (varsayılan giriş `admin` / `DevOps2026!`):

```bash
cd ~/jenkins-labs/lab-01-jenkins-docker-setup/b-kod
docker network create kind 2>/dev/null || true
docker compose up -d --build
```

### 3. Çekirdek Laboratuvarlara Başlama
```bash
cd ~/jenkins-labs/lab-01-jenkins-docker-setup
cat README.md
```
