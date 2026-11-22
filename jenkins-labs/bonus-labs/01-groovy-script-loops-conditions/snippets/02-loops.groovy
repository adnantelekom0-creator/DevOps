pipeline {
    agent any
    stages {
        stage('Loop Usage') {
            steps {
                script {
                    echo "=== For Dongusu Ornegi ==="
                    for (int i = 1; i <= 5; i++) {
                        echo "Iterasyon #${i} - Islem Tamamlandi"
                    }

                    echo "=== Koleksiyon Uzerinde Dongu ==="
                    def environments = ['development', 'staging', 'production']
                    for (envName in environments) {
                        echo "Hedef Ortam: ${envName}"
                    }
                }
            }
        }
    }
}
