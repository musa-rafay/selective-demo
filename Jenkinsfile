/*
 * Minimal selective-deploy pipeline
 * - Params include testbed/user/org + AUTO-GENERATED console URLs
 * - Detect changed services (vs target branch of PR)
 * - Echo services list
 * - SSH into VM (noop) and exit 0
 */

pipeline {
  agent any
  options { timestamps() }

  parameters {
    string(  name: 'testbed_name',     defaultValue: 'stest',  description: 'Test Bed Name')
    string(  name: 'console_url',      defaultValue: '',       description: 'Autofilled from testbed_name if blank')
    string(  name: 'ops_console_url',  defaultValue: '',       description: 'Autofilled from testbed_name if blank')
    string(  name: 'organization_name',defaultValue: 'rafay',  description: 'Organization/Env name')
    string(  name: 'username',         defaultValue: 'example@rafay.co', description: ' username ')
    string(  name: 'password',         defaultValue: 'changeplz',       description: ' password ')
  }

  environment {
    // Map repo dirs -> short service names
    SERVICE_MAP = 'service-alpha:alpha,service-bravo:bravo'

    // SSH bits 
    VM_HOST     = 'ubuntu@144.24.6.170'          
    SSH_CRED_ID = 'testbed-vm-ssh'             
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Compute/echo params') {
      steps {
        script {
          env.CONSOLE_URL     = (params.console_url?.trim())     ?: "console-${params.testbed_name}.dev.rafay-edge.net"
          env.OPS_CONSOLE_URL = (params.ops_console_url?.trim()) ?: "ops-console-${params.testbed_name}.dev.rafay-edge.net"

          echo """\
testbed_name      = ${params.testbed_name}
organization_name = ${params.organization_name}
username          = ${params.username}
console_url       = ${env.CONSOLE_URL}
ops_console_url   = ${env.OPS_CONSOLE_URL}
"""
        }
      }
    }

   stage('Resolve latest release info') {
  steps {
    script {
      withCredentials([usernamePassword(credentialsId: 'musa-rafay',
                                        usernameVariable: 'GUSER',
                                        passwordVariable: 'GPASS')]) {
        try {
          def branchLines = sh(returnStdout: true, script: '''
            #!/bin/bash
            set -euo pipefail
            REPO="github.com/RafaySystems/rafay-hub.git"
            git ls-remote --heads https://$GUSER:$GPASS@$REPO \
              | awk '{print $2}' | sed 's#refs/heads/##'
          ''').trim().split('\\n')

          echo "Remote branches:\n${branchLines.join('\n')}"

          def versionRegex = ~/v\\d+\\.\\d+\\.x/
          def candidates = []

          branchLines.each { br ->
            def m = (br =~ versionRegex)
            if (m.find()) {
              candidates << [branch: br, token: m.group()]
            }
          }

          if (!candidates) {
            echo "WARN: No branches containing vX.Y.x token found → skipping."
            return
          }

          def sorted = candidates.sort { a, b ->
            def av = a.token.replace('v','').replace('.x','').split('\\.').collect { it as int }
            def bv = b.token.replace('v','').replace('.x','').split('\\.').collect { it as int }
            for (int i=0; i<Math.min(av.size(), bv.size()); i++) {
              if (av[i] != bv[i]) return av[i] <=> bv[i]
            }
            av.size() <=> bv.size()
          }

          def latest = sorted.last()
          env.LATEST_QC_REL_BRANCH = latest.branch
          env.LATEST_QC_REL_TOKEN  = latest.token

          echo "Picked branch '${env.LATEST_QC_REL_BRANCH}' (token ${env.LATEST_QC_REL_TOKEN})"

          def url = "https://jenkins-wh.ops.rafay-edge.net/job/platform-pipelines/job/rctl/job/${env.LATEST_QC_REL_BRANCH}/lastStableBuild/api/json"
          def json = sh(returnStdout: true, script: "curl -sf ${url} || true").trim()
          if (!json) {
            echo "WARN: Could not fetch lastStableBuild for ${env.LATEST_QC_REL_BRANCH}"
            return
          }

          def parsed = new groovy.json.JsonSlurper().parseText(json)
          env.LATEST_RCTL_BUILD_NUMBER = parsed.number.toString()

          echo "Last stable build #: ${env.LATEST_RCTL_BUILD_NUMBER}"
        } catch (err) {
          echo "⚠️  Failed to resolve latest release info: ${err}"
        }
      }
    }
  }
}
    stage('Detect changes') {
      when { changeRequest() }   // run only for PRs
      steps {
        script {
          // Fetch all heads so origin/<target> exists
          sh 'git fetch origin +refs/heads/*:refs/remotes/origin/* --quiet'

          def target = env.CHANGE_TARGET ?: 'main'
          def base = sh(returnStdout: true,
                        script: "git merge-base origin/${target} HEAD").trim()

          def changed = sh(returnStdout: true, script: """
            git diff --name-only ${base}...HEAD | cut -d/ -f1 | sort -u | tr -d '\\r'
          """).trim()

          def folders = changed ? changed.split('\\n') : []
          def map = SERVICE_MAP.split(',').collectEntries{ it.split(':') }
          def impacted = folders.collect { map[it] }.findAll { it }

          env.SVC_LIST = impacted ? impacted.join(',') : 'NONE'
          echo "Services to patch => ${env.SVC_LIST}"
        }
      }
    }

    stage('SSH to VM (noop)') {
      when { expression { env.SVC_LIST != null } }
      steps {
        sshagent(credentials: [env.SSH_CRED_ID]) {
          sh """
            ssh -o StrictHostKeyChecking=no ${env.VM_HOST} '
              echo "Jenkins connected.";
              echo "Services: ${env.SVC_LIST}";
              echo "Console: ${env.CONSOLE_URL}";
              echo "OpsConsole: ${env.OPS_CONSOLE_URL}";
              exit 0
            '
          """
        }
      }
    }
  }

  post {
    success { echo '✅ Done.' }
    failure { echo '❌ Pipeline failed.' }
  }
}
