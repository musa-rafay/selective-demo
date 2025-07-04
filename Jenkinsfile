/*
 * Jenkinsfile – selective-deploy demo (no helper Docker image)
 * -----------------------------------------------------------
 * - Two toy micro-services:  service-alpha  &  service-bravo
 * - One always-on test-bed container (testbed-alpha-bravo)
 * - Pipeline locks the bed, patches only the changed service(s),
 *   runs smoke + service tests once, then releases the bed.
 */

pipeline {
  agent any

  parameters {
	booleanParam(name: 'RUN_AGAIN', defaultValue: false, description: 'Re-run tests without new approval')
  }

  /* only ONE build at a time may own a test-bed with label `edgesrv` */
  options { lock(label: 'edgesrv', quantity: 1) }

  environment {
    BED_NAME = 'testbed-alpha-bravo'   // dummy bed container name
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
                echo 'Previous run was green and RUN_AGAIN is false → skipping.'
                currentBuild.result = 'SUCCESS'
                return          
            }
         }
      }
    }
	  
    stage('Build artefacts (stub)') {
      steps { sh 'echo "Pretend build – nothing to compile"' }
    }

    /* now runs on the controller – no Docker agent */
    stage('Generate stable-builds.yml') {
      steps {
        sh '''
          # verify PyYAML is present; install once if missing
          python3 - <<'PY'
import importlib, subprocess, sys
try:
    importlib.import_module("yaml")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "--break-system-packages",
                           "install", "--quiet", "PyYAML"])
PY
          python3 ci/gen_stable_builds.py
        '''
        archiveArtifacts artifacts: 'stable-builds.yml', fingerprint: true
      }
    }

  stage('Detect changes -> SVC_LIST') {
   steps {
     script {
      // Make sure we have main's commit history
      sh 'git fetch --no-tags origin main'

      // Use merge-base to find the true common ancestor
      def base = sh(returnStdout: true,
                    script: 'git merge-base FETCH_HEAD HEAD').trim()

      def folders = sh(returnStdout: true,
                       script: "git diff --name-only ${base}...HEAD | cut -d/ -f1 | sort -u")
                       .trim()
                       .split('\n')

      def map = [ 'service-alpha':'alpha', 'service-bravo':'bravo' ]
      def impacted = folders.collect { map[it] }.findAll { it }
      env.SVC_LIST = impacted ? impacted.join(',') : 'alpha,bravo'
      echo "Services to patch / test => ${env.SVC_LIST}"
      }
    }
  }

    stage('Deploy only changed services') {
      steps { sh "ci/deploy_changed.sh ${env.BED_NAME} ${env.SVC_LIST}" }
    }

    stage('Integration tests (parallel inside bed)') {
      steps { sh "ci/run_tests.sh ${env.SVC_LIST}" }
    }
  }

  post {
    success { echo '✅  All tests passed – merge allowed.' }
    failure { echo '❌  Tests failed – fix code or re-run.' }
  }
}
