#!/usr/bin/env groovy

/**
 * Bütün pipeline'larda aynı biçimde durum mesajı yazar.
 * Kullanım: notifyStatus(status: 'SUCCESS', message: 'Build tamamlandı')
 */
def call(Map config = [:]) {
    def status = config.get('status', 'INFO')
    def msg = config.get('message', 'Pipeline adımı çalıştı')
    echo "[NOTIFICATION-${status}] Job: ${env.JOB_NAME} #${env.BUILD_NUMBER} | Mesaj: ${msg}"
}
