pipeline {
    agent any
    parameters {
        choice(name: 'TARGET_ENV', choices: ['dev', 'prod'], description: 'Dagitim ortami')
    }
    stages {
        stage('Condition Usage') {
            steps {
                script {
                    if (params.TARGET_ENV == 'prod') {
                        echo "DIKKAT: Production ortamina ozel guvenlik kontrolleri devrede."
                    } else {
                        echo "BILGI: Gelistirme ortamina hizli gecis yapiliyor."
                    }
                }
            }
        }
    }
}
