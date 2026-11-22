pipelineJob('01-hello-jcasc') {
  displayName('01 - Hello Jenkins as Code')
  description('JCasC açılışta bu jobu otomatik oluşturur. UI ile job konfigürasyonu yapılmaz.')
  definition {
    cps {
      script('''
        pipeline {
          agent any
          stages {
            stage('Merhaba') {
              steps {
                echo "Merhaba! Job: ${env.JOB_NAME}, build: #${env.BUILD_NUMBER}"
              }
            }
          }
        }
      '''.stripIndent())
      sandbox()
    }
  }
}
