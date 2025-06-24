pipeline {
  agent any
  options { lock(label: 'edgesrv', quantity: 1) }

  stages {
    stage('Checkout & Build') { steps { checkout scm } }

    stage('Generate stable-builds.yml') {
      steps { 
	sh '''
	  sudo apt-get update
	  sudo apt-get install -y python3-yaml
	  python3 ci/gen_stable_builds.py
	'''
	 }
    }

    stage('Detect changes') {
      steps {
        script {
          def changed = sh(returnStdout: true,
              script: "git diff --name-only origin/main...HEAD | cut -d/ -f1 | sort -u")
              .trim().split('\n')
          def map = [ 'service-alpha':'alpha', 'service-bravo':'bravo' ]
          env.SVC_LIST = changed.collect { map[it] }.findAll { it }.join(',')
          if (!env.SVC_LIST) { env.SVC_LIST = 'alpha,bravo' }  // default smoke
          echo "Services to patch/test: ${env.SVC_LIST}"
        }
      }
    }

    stage('Deploy & Test (locked bed)') {
      steps {
        sh "ci/deploy_changed.sh testbed-alpha-bravo ${env.SVC_LIST}"
        sh "ci/run_tests.sh ${env.SVC_LIST}"
      }
    }
  }

  post {
    success { echo 'Tests passed' }
    failure { echo 'Tests failed' }
  }
}
