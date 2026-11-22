pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '7'))
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        retry(1)
    }
    stages {
        stage('Options Stage') {
            steps {
                echo "This build has timestamps enabled and max 5 builds kept."
            }
        }
    }
}
