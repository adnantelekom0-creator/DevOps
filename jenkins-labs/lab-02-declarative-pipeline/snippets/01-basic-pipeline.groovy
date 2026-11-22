pipeline {
    agent any
    stages {
        stage('Build stage') {
            steps {
                echo "This is build stage"
            }
        }
        stage('Test stage') {
            steps {
                echo "This is test stage"
            }
        }
        stage('Deploy stage') {
            steps {
                echo "This is deploy stage"
            }
        }
    }
}
