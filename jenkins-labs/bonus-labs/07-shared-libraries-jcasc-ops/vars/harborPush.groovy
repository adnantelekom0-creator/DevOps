#!/usr/bin/env groovy

/**
 * Yerel image'ı Harbor'a gönderir.
 * Kullanım: harborPush(image: 'order-service', tag: '1.5.0')
 * Varsayılanlar LAB-JEN-04 ile aynıdır: 127.0.0.1:18444, proje devops-public, credential harbor-creds.
 */
def call(Map config = [:]) {
    def registry = config.get('registry', '127.0.0.1:18444')
    def project  = config.get('project', 'devops-public')
    def image    = config.get('image', 'demo-app')
    def tag      = config.get('tag', 'latest')
    def credsId  = config.get('credentialsId', 'harbor-creds')

    def target = "${registry}/${project}/${image}:${tag}"
    echo "[SHARED-LIB-HARBOR] ${image}:${tag} -> ${target}"

    withCredentials([usernamePassword(credentialsId: credsId, usernameVariable: 'H_USER', passwordVariable: 'H_PASS')]) {
        sh """
            set -eu
            printf '%s' "\${H_PASS}" | docker login ${registry} -u "\${H_USER}" --password-stdin
            docker tag ${image}:${tag} ${target}
            docker push ${target}
            docker logout ${registry}
        """
    }
    echo "[SHARED-LIB-HARBOR] Push tamamlandı: ${target}"
}
