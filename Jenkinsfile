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
    string(  name: 'username',         defaultValue: 'ubuntu', description: 'VM username (for SSH stage)')
    password(name: 'password',         defaultValue: '',       description: 'VM password (unused if ssh key)')
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

  }
}
