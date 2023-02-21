pipeline {
  agent {
    node { label 'master' }
  }
  stages {

    stage('Build frontend Image') {
        steps {
          script {
            docker.withRegistry(registryUrl, registryCredential ) {
               docker.build(dockerRegistry + ":v${env.BUILD_ID}"," -f ./Dockerfile .").push()
            }
          }
        }
    }

    stage('Remove Unused docker image') {
      steps {
        sh "docker rmi ${dockerRegistry}:v${env.BUILD_ID} || true"
      }
    }

  }
  environment {
    dockerRegistry= 'donglog/myflaskapp'
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '15'))
    disableConcurrentBuilds()
  }
  triggers {
   pollSCM('H/2 * * * *')
    }
  }
}
