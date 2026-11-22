pipelineJob('03-environment-jcasc') {
  displayName('03 - Environment ve Koşul')
  description('Jenkinsfile ortam değişkeni ve when koşulu için küçük Jenkins as Code örneği.')
  definition {
    cps {
      script('''
        pipeline {
          agent any
          environment {
            APPLICATION = 'hello-service'
            DEPLOY_ENV = 'test'
          }
          stages {
            stage('Bilgi') {
              steps {
                echo "Uygulama: ${env.APPLICATION}, ortam: ${env.DEPLOY_ENV}"
              }
            }
            stage('Test Ortamı Mesajı') {
              when { expression { env.DEPLOY_ENV == 'test' } }
              steps {
                echo 'Koşul sağlandı: test ortamı adımı çalıştı.'
              }
            }
          }
        }
      '''.stripIndent())
      sandbox()
    }
  }
}
