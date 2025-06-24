/*
 * Jenkinsfile – selective-deploy demo
 * - Two toy micro-services:  service-alpha  &  service-bravo
 * - One always-on test-bed container running on the same Docker network
 * - Pipeline locks the bed, patches only the changed service(s),
 *   runs smoke + service tests once, then releases the bed.
 */

pipeline {
  /* any executor on the controller is fine for this demo */
  agent any

  /* only ONE build at a time may own a test-bed with label `edgesrv` */
  options {
    lock(label: 'edgesrv', quantity: 1)
  }

  /* handy constants */
  environment {
    BED_NAME = 'testbed-alpha-bravo'      // name of the dummy bed container
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build artefacts (stub)') {
      steps {
        sh 'echo "Pretend build – nothing to compile for shell scripts"'
      }
    }

    /* Use a throw-away Python image so we always have PyYAML available */
    stage('Generate stable-builds.yml') {
      agent {
        docker {
          image 'python:3.12-slim'
          reuseNode true                  // mount same workspace
          args '-u root:root'             // run as root so we can pip install
        }
      }
      steps {
        sh '''
          pip install --quiet pyyaml
          python ci/gen_stable_builds.py
        '''
        archiveArtifacts artifacts: 'stable-builds.yml', fingerprint: true
      }
    }

    stage('Detect changes -> SVC_LIST') {
      steps {
        script {
          /* list unique top-level folders changed vs. main */
          def diff = sh(returnStdout: true,
              script: "git diff --name-only origin/main...HEAD | cut -d/ -f1 | sort -u")
              .trim()
          def folders = diff ? diff.split('\\n') : []
          /* map folder → service id */
          def folderToSvc = [
            'service-alpha': 'alpha',
            'service-bravo': 'bravo'
          ]
          def impacted = folders.collect { folderToSvc[it] }.findAll { it }
          env.SVC_LIST = impacted ? impacted.join(',') : 'alpha,bravo'  // smoke-only -> test both
          echo "Services to patch / test => ${env.SVC_LIST}"
        }
      }
    }

    stage('Deploy only changed services') {
      steps {
        sh "ci/deploy_changed.sh ${env.BED_NAME} ${env.SVC_LIST}"
      }
    }

    stage('Integration tests (parallel inside bed)') {
      steps {
        sh "ci/run_tests.sh ${env.SVC_LIST}"
      }
    }
  }

  post {
    success { echo '  All tests passed – merge allowed.' }
    failure { echo '  Tests failed – fix code or manually re-run.' }
  }
}
