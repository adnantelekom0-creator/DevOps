pipeline {
    agent any
    parameters {
        string(name: 'APP_VERSION', defaultValue: '1.0.0', description: 'Uygulama surum numarasi')
        choice(name: 'DEPLOY_ENV', choices: ['dev', 'qa', 'prod'], description: 'Hedef dagitim ortami')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Testler kosturulsun mu?')
    }
    stages {
        stage('Parameters Demo') {
            steps {
                echo "Surum           : ${params.APP_VERSION}"
                echo "Hedef Ortam     : ${params.DEPLOY_ENV}"
                echo "Test Kosulsun mu: ${params.RUN_TESTS}"
            }
        }
    }
}
