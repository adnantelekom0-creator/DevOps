#!/usr/bin/env bash
set -euo pipefail

# Jenkins container içinde çalıştırılır; depo Jenkins'in görebildiği jenkins_home volume'üne kurulur.
TARGET_DIR="${1:-/var/jenkins_home/sample-multibranch-repo.git}"
WORK_DIR="$(mktemp -d)"

echo "=== Multibranch Pipeline İçin Çok Dallı Git Deposu Hazırlanıyor ==="
echo "Hedef Depo Yolu: ${TARGET_DIR}"

rm -rf "${TARGET_DIR}"

# 1. Bare git repository oluştur
mkdir -p "${TARGET_DIR}"
git init --bare "${TARGET_DIR}"

# 2. Geçici çalışma ağacı aç ve ana dalı başlat
mkdir -p "${WORK_DIR}"
cd "${WORK_DIR}"
git init
git config user.name "DevOps Engineer"
git config user.email "engineer@devopsatolyesi.local"
git remote add origin "${TARGET_DIR}"

# Jenkinsfile kopyala
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "${SCRIPT_DIR}/../Jenkinsfile" .

# main dalı
git checkout -b main
git add Jenkinsfile
git commit -m "feat: main branch ilk kurulum"
git push origin main

# develop dalı
git checkout -b develop
sed -i.bak 's/APP_NAME = '\''multibranch-demo-app'\''/APP_NAME = '\''multibranch-demo-app-develop'\''/' Jenkinsfile || sed -i '' 's/APP_NAME = '\''multibranch-demo-app'\''/APP_NAME = '\''multibranch-demo-app-develop'\''/' Jenkinsfile
rm -f Jenkinsfile.bak
git add Jenkinsfile
git commit -m "feat: develop dali guncellendi"
git push origin develop

# feature/login dalı
git checkout -b feature/login
sed -i.bak 's/APP_NAME = '\''multibranch-demo-app-develop'\''/APP_NAME = '\''multibranch-demo-app-feature-login'\''/' Jenkinsfile || sed -i '' 's/APP_NAME = '\''multibranch-demo-app-develop'\''/APP_NAME = '\''multibranch-demo-app-feature-login'\''/' Jenkinsfile
rm -f Jenkinsfile.bak
git add Jenkinsfile
git commit -m "feat: login ozelligi gelistirildi"
git push origin feature/login

# Temizlik
cd /
rm -rf "${WORK_DIR}"

echo ""
echo "=== Depo Hazırlığı Başarıyla Tamamlandı ==="
echo "Yerel Depo Adresi: ${TARGET_DIR}"
echo "Oluşturulan Dallar: main, develop, feature/login"
