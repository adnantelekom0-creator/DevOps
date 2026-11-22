pipelineJob('02-parameters-jcasc') {
  displayName('02 - Build Parameters')
  description('Parametreler Job DSL ile oluşturulur; kullanıcı doğrudan Build with Parameters seçeneğini çalıştırır.')
  parameters {
    stringParam('NAME', 'DevOps Mühendisi', 'Ekrana yazılacak isim')
    choiceParam('ENVIRONMENT', ['development', 'test', 'production'], 'Hedef ortam örneği')
    booleanParam('SHOW_DATE', true, 'Tarihi konsola yaz')
  }
  definition {
    cps {
      script('''
        pipeline {
          agent any
          stages {
            stage('Parametreleri Kullan') {
              steps {
                script {
                  if (!params.NAME?.trim()) {
                    error('NAME boş bırakılamaz.')
                  }
                  echo "Merhaba ${params.NAME}; ortam: ${params.ENVIRONMENT}"
                  if (params.SHOW_DATE) {
                    sh 'date -u'
                  }
                }
              }
            }
          }
        }
      '''.stripIndent())
      sandbox()
    }
  }
}
