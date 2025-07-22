/*
 * Jenkinsfile – selective-deploy demo (Docker agent)
 * --------------------------------------------------
 * - Two toy micro-services: service-alpha & service-bravo
 * - One always-on dummy "testbed" Docker container (BED_NAME)
 * - Lock ensures only one build owns the bed at a time
 * - Only changed services are patched & tested
 */

pipeline {
  agent {
    docker {
      image 'python:3.11-slim'          // has python & pip
      args  '-u root --network host'    // root for apt; host net so kubectl/ssh works if needed
    }
  }

  parameters {
    booleanParam(name: 'RUN_AGAIN', defaultValue: false,
                 description: 'Re-run tests without new approval')
  }

  options { lock(label: 'edgesrv', quantity: 1) }

  environment {
    BED_NAME = 'testbed-alpha-bravo'
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Skip-gate (previous build green)') {
      when { expression { !params.RUN_AGAIN } }
      steps {
        script {
          if (currentBuild.getPreviousBuild()?.result == 'SUCCESS') {
            echo 'Previous run was green & RUN_AGAIN=false → skipping.'
            currentBuild.result = 'SUCCESS'
            return
          }
        }
      }
    }

    stage('Setup deps (PyYAML etc.)') {
      steps {
        sh '''
          set -euo pipefail
          python -m pip install --quiet PyYAML
          # add any other libs here
        '''
      }
    }

    stage('Build artefacts (stub)') {
      steps { sh 'echo "Pretend build – nothing to compile"' }
    }

    stage('Generate stable-builds.yml') {
      steps {
        sh 'python ci/gen_stable_builds.py'
        archiveArtifacts artifacts: 'stable-builds.yml', fingerprint: true
      }
    }

    stage('Detect changes -> SVC_LIST') {
      steps {
        script {
          sh 'git fetch --no-tags origin main'
          def base = sh(returnStdout: true,
                        script: 'git merge-base FETCH_HEAD HEAD').trim()
          def changed = sh(returnStdout: true, script: """
            git diff --name-only ${base}...HEAD | cut -d/ -f1 | sort -u | tr -d '\\r'
          """).trim()
          def folders = changed ? changed.split('\\n') : []
          def map = [ 'service-alpha':'alpha', 'service-bravo':'bravo' ]
          def impacted = folders.collect { map[it] }.findAll { it }
          env.SVC_LIST = impacted ? impacted.join(',') : 'alpha,bravo'
          echo "Services to patch / test => ${env.SVC_LIST}"
        }
      }
    }

    stage('Deploy only changed services') {
      when { expression { env.SVC_LIST } }
      steps {
        sh "ci/deploy_changed.sh ${env.BED_NAME} ${env.SVC_LIST}"
      }
    }

    stage('Integration tests (inside bed)') {
      steps {
        sh "ci/run_tests.sh ${env.SVC_LIST}"
      }
    }
  }

  post {
    success { echo '✅  All tests passed – merge allowed.' }
    failure { echo '❌  Tests failed – fix code or re-run.' }
  }
}
