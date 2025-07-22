pipeline {
  agent any

  parameters {
    string(name: 'testbed_name',      defaultValue: 'mytb',      description: 'Testbed name')
    string(name: 'username',          defaultValue: 'user',      description: 'Username for VM')
    password(name: 'password',        defaultValue: '',          description: 'Password for VM')
    string(name: 'organization_name', defaultValue: 'rafay',     description: 'Org name for context')
  }

  environment {
    console_url     = "console-${params.testbed_name}.dev.rafay-edge.net"
    ops_console_url = "ops-console-${params.testbed_name}.dev.rafay-edge.net"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Compute/echo params') {
      steps {
        script {
          echo "testbed_name      = ${params.testbed_name}"
          echo "organization_name = ${params.organization_name}"
          echo "username          = ${params.username}"
          echo "console_url       = ${env.console_url}"
          echo "ops_console_url   = ${env.ops_console_url}"
        }
      }
    }

    stage('Resolve latest release info') {
      steps {
        script {
          withCredentials([
            usernamePassword(credentialsId: 'musa-rafay',
                             usernameVariable: 'GUSER',
                             passwordVariable: 'GPASS')
          ]) {
            def branchLines = sh(returnStdout: true, script: """
              bash -c '
                set -euo pipefail
                REPO="github.com/RafaySystems/rafay-hub.git"
                git ls-remote --heads https://\$GUSER:\$GPASS@\$REPO \\
                  | awk \'{print \$2}\' | sed \'s#refs/heads/##\'
              '
            """).trim().split('\\n')

            def filtered = branchLines.findAll { it ==~ /^v\\d+\\.\\d+\\.x$/ }
            if (!filtered) error "No release branches found"

            def sorted = filtered.sort { a, b ->
              def av = a.replace('v','').replace('.x','').split('\\.').collect{ it as int }
              def bv = b.replace('v','').replace('.x','').split('\\.').collect{ it as int }
              for (int i = 0; i < Math.min(av.size(), bv.size()); i++) {
                if (av[i] != bv[i]) return av[i] <=> bv[i]
              }
              return av.size() <=> bv.size()
            }

            env.LATEST_QC_REL_BRANCH = sorted.last()

            def url = "https://jenkins-wh.ops.rafay-edge.net/job/platform-pipelines/job/rctl/job/${env.LATEST_QC_REL_BRANCH}/lastStableBuild/api/json"
            def json = sh(returnStdout: true, script: "curl -s ${url}").trim()
            def parsed = new groovy.json.JsonSlurper().parseText(json)

            env.LATEST_RCTL_BUILD_NUMBER = parsed.number.toString()

            echo "Latest branch: ${env.LATEST_QC_REL_BRANCH}"
            echo "Last stable build #: ${env.LATEST_RCTL_BUILD_NUMBER}"
          }
        }
      }
    }

    stage('Detect changes') {
      steps {
        script {
          sh 'git fetch origin main --quiet'
          def base = sh(returnStdout: true, script: 'git merge-base origin/main HEAD').trim()
          def folders = sh(returnStdout: true, script: "git diff --name-only ${base}...HEAD | cut -d/ -f1 | sort -u").trim().split('\n')
          def map = [ 'service-alpha': 'alpha', 'service-bravo': 'bravo' ]
          def impacted = folders.collect { map[it] }.findAll { it }
          env.SVC_LIST = impacted ? impacted.join(',') : 'alpha,bravo'
          echo "Services to patch/test: ${env.SVC_LIST}"
        }
      }
    }

    stage('SSH to VM (noop)') {
      steps {
        echo "Would SSH into VM as ${params.username} (noop)"
        // ssh commands here if needed
      }
    }
  }

  post {
    success {
      echo "✅ Pipeline succeeded"
    }
    failure {
      echo "❌ Pipeline failed"
    }
  }
}
