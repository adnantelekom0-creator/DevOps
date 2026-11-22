#!/bin/bash
# ArgoCD API ile: oturum aç, Application'ın image ayarını değiştir, sync başlat, Synced + Healthy bekle.
# Kullanım: ARGOCD_URL=... ARGOCD_USER=... ARGOCD_PASS=... ./argocd-sync.sh <uygulama> <image>
set -euo pipefail

APP="${1:?uygulama adi gerekli}"
IMAGE="${2:?image gerekli (or. kullanici/devops-app-public:v2-abc1234)}"
: "${ARGOCD_URL:?ARGOCD_URL gerekli}" "${ARGOCD_USER:?}" "${ARGOCD_PASS:?}"

# ArgoCD kendinden imzalı sertifika kullanır; -k bu yüzden
TOKEN=$(curl -sk -X POST "${ARGOCD_URL}/api/v1/session" -H 'Content-Type: application/json' \
  -d "{\"username\":\"${ARGOCD_USER}\",\"password\":\"${ARGOCD_PASS}\"}" | perl -MJSON::PP -0777 -ne 'print decode_json($_)->{token} // ""')
[ -n "${TOKEN}" ] || { echo "ArgoCD oturumu acilamadi" >&2; exit 1; }
AUTH="Authorization: Bearer ${TOKEN}"

echo "Image ayari: devops-app=${IMAGE}"
curl -skf -X PATCH "${ARGOCD_URL}/api/v1/applications/${APP}" -H "${AUTH}" -H 'Content-Type: application/json' \
  -d "{\"name\":\"${APP}\",\"patchType\":\"merge\",\"patch\":\"{\\\"spec\\\":{\\\"source\\\":{\\\"kustomize\\\":{\\\"images\\\":[\\\"devops-app=${IMAGE}\\\"]}}}}\"}" >/dev/null

echo "Sync baslatiliyor"
curl -skf -X POST "${ARGOCD_URL}/api/v1/applications/${APP}/sync" -H "${AUTH}" -H 'Content-Type: application/json' -d '{}' >/dev/null

for i in $(seq 1 60); do
  STATE=$(curl -skf "${ARGOCD_URL}/api/v1/applications/${APP}" -H "${AUTH}")
  # Uygulama seviyesindeki durum: .status.sync.status ve .status.health.status
  SYNC=$(printf '%s' "${STATE}" | perl -MJSON::PP -0777 -ne 'print decode_json($_)->{status}{sync}{status} // ""')
  HEALTH=$(printf '%s' "${STATE}" | perl -MJSON::PP -0777 -ne 'print decode_json($_)->{status}{health}{status} // ""')
  echo "Durum: sync=${SYNC:-?} health=${HEALTH:-?}"
  if [ "${SYNC}" = "Synced" ] && [ "${HEALTH}" = "Healthy" ]; then
    echo "Uygulama Synced ve Healthy"
    exit 0
  fi
  sleep 5
done
echo "Uygulama 5 dakikada Synced/Healthy olmadi" >&2
exit 1
