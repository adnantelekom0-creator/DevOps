#!/bin/bash
# GitLab'ın push olayında gönderdiği isteğin aynısını Jenkins'in GitLab eklentisi adresine yollar.
# Kullanım: SECRET_TOKEN='<job ayarındaki token>' ./scripts/simulate-webhook.sh <job-adı>
set -euo pipefail

JENKINS_URL="${JENKINS_URL:-http://127.0.0.1:18080}"
JOB_NAME="${1:-gitlab-webhook-demo}"
WEBHOOK_ENDPOINT="${JENKINS_URL}/project/${JOB_NAME}"
: "${SECRET_TOKEN:?SECRET_TOKEN tanimli degil - job ayarinda Generate ile uretilen degeri verin}"

echo "Hedef: ${WEBHOOK_ENDPOINT}"

# GitLab Push Hook gövdesi (GitLab'ın gönderdiği alanların kısaltılmış hâli)
PAYLOAD='{
  "object_kind": "push",
  "event_name": "push",
  "before": "0000000000000000000000000000000000000000",
  "after": "95790bf891e76fee5e1747ab5899de4a7f18524c",
  "ref": "refs/heads/main",
  "checkout_sha": "95790bf891e76fee5e1747ab5899de4a7f18524c",
  "user_id": 1,
  "user_name": "DevOps Engineer",
  "user_username": "root",
  "user_email": "engineer@example.com",
  "project_id": 15,
  "project": {
    "id": 15,
    "name": "novashop-order-service",
    "namespace": "root",
    "path_with_namespace": "root/novashop-order-service",
    "default_branch": "main",
    "git_ssh_url": "git@gitlab.example.com:root/novashop-order-service.git",
    "web_url": "http://gitlab.example.com/root/novashop-order-service",
    "git_http_url": "http://gitlab.example.com/root/novashop-order-service.git"
  },
  "repository": {
    "name": "novashop-order-service",
    "url": "http://gitlab.example.com/root/novashop-order-service.git",
    "homepage": "http://gitlab.example.com/root/novashop-order-service",
    "git_http_url": "http://gitlab.example.com/root/novashop-order-service.git",
    "git_ssh_url": "git@gitlab.example.com:root/novashop-order-service.git"
  },
  "commits": [
    {
      "id": "95790bf891e76fee5e1747ab5899de4a7f18524c",
      "message": "feat: add order checkout endpoint",
      "timestamp": "2026-09-19T10:00:00Z",
      "author": {"name": "DevOps Engineer", "email": "engineer@example.com"}
    }
  ],
  "total_commits_count": 1
}'

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${WEBHOOK_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -H "X-Gitlab-Event: Push Hook" \
  -H "X-Gitlab-Token: ${SECRET_TOKEN}" \
  -d "${PAYLOAD}")

echo "HTTP ${HTTP_CODE}"
if [ "${HTTP_CODE}" = "200" ]; then
    echo "Jenkins isteği kabul etti; job tetiklendi."
else
    echo "Jenkins isteği kabul etmedi (token ve job adını kontrol edin)." >&2
    exit 1
fi
