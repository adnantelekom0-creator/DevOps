pipeline {
    agent any
    stages {
        stage('Built-in Variables') {
            steps {
                echo "Job Name        : ${env.JOB_NAME}"
                echo "Build Number    : ${env.BUILD_NUMBER}"
                echo "Build ID        : ${env.BUILD_ID}"
                echo "Build URL       : ${env.BUILD_URL}"
                echo "Node Name       : ${env.NODE_NAME}"
                echo "Workspace Path  : ${env.WORKSPACE}"
            }
        }
    }
}
