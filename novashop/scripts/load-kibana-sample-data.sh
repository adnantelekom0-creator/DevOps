#!/usr/bin/env bash
# ==============================================================================
# NovaShop — Kibana Hazır Örnek Veri (Sample Data) Yükleme Betiği
# Kapsam: eCommerce Sipariş Logları & Web Server Erişim Logları
# ==============================================================================

set -euo pipefail

KIBANA_URL="${1:-http://localhost:15601}"
echo "==> Kibana Hazır Örnek Veri Setleri Yükleniyor: $KIBANA_URL"

# Kibana hazır olana kadar bekle
until curl -s -f -H 'kbn-xsrf: true' "$KIBANA_URL/api/status" > /dev/null; do
    echo "    Kibana bekleniyor ($KIBANA_URL)..."
    sleep 3
done

load_sample() {
    local dataset="$1"
    local desc="$2"
    echo "==> Yükleniyor: $desc ($dataset)..."
    local response
    local code
    code=$(curl -s -o /tmp/kibana-sample-$dataset.json -w '%{http_code}' -X POST -H "kbn-xsrf: true" "$KIBANA_URL/api/sample_data/$dataset")
    echo "    HTTP $code"
    if [ "$code" != "200" ]; then
        echo "❌ HATA: $desc yüklenemedi: $(head -c 300 /tmp/kibana-sample-$dataset.json)" >&2
        exit 1
    fi
}

# 1. E-Ticaret Sipariş Veri Seti (Grafikler, Gelir Panosu, Müşteri Siparişleri)
load_sample "ecommerce" "Kibana Sample eCommerce Data"

# 2. Web Sunucusu Erişim Günlükleri (HTTP 200/404/500, Coğrafi Harita, Trafik)
load_sample "logs" "Kibana Sample Web Access Logs"

echo "=============================================================================="
echo "✅ Hazır örnek veri setleri ve panolar başarıyla yüklendi!"
echo "   Kibana Dashboards sekmesinden [eCommerce] Revenue Dashboard ve"
echo "   [Logs] Web Traffic Dashboard panolarını doğrudan inceleyebilirsiniz."
echo "=============================================================================="
