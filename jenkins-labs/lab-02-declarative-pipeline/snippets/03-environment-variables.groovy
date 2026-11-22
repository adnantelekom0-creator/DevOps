pipeline {
    agent any
    environment {
        APP_NAME    = 'my-microservice'
        APP_ENV     = 'staging'
        PORT_NUMBER = '8080'
    }
    stages {
        stage('Environment Usage') {
            steps {
                echo "Deploying application: ${env.APP_NAME}"
                echo "Target environment  : ${env.APP_ENV}"
                echo "Service port        : ${env.PORT_NUMBER}"
            }
        }
    }
}
