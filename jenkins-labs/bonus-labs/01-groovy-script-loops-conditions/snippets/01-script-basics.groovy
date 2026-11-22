pipeline {
    agent any
    stages {
        stage('Script Usage') {
            steps {
                script {
                    def age = 25
                    def multiplier = 2
                    def calculatedResult = age * multiplier
                    echo "Hesaplanan Deger: ${calculatedResult}"
                }
            }
        }
    }
}
