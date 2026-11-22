pipeline {
    agent any
    stages {
        stage('Execution Stage') {
            steps {
                echo "Pipeline adimlari icra ediliyor..."
            }
        }
    }
    post {
        always {
            echo "[POST: ALWAYS] Bu blok build sonucu ne olursa olsun (basarili/hatali) daima calisir."
        }
        success {
            echo "[POST: SUCCESS] Tebrikler! Tum asamalar basariyla tamamlandi."
        }
        failure {
            echo "[POST: FAILURE] Dikkat! Asamalardan biri basarisiz oldu."
        }
        cleanup {
            echo "[POST: CLEANUP] Gecici dosyalar ve calisma alani temizlendi."
        }
    }
}
