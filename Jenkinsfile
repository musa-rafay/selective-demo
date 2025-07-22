pipeline {
  agent any

  options { timestamps() }

  environment {
    // Map repo folders → short service names
    SERVICE_MAP = 'service-alpha:alpha,service-bravo:bravo'
    VM_HOST     = 'ubuntu@144.24.6.170'          // <-- change me
    SSH_CRED_ID = 'testbed-vm-ssh'             // <-- Jenkins SSH username/privkey credential id
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    // Only run for PRs. If you’re using a multibranch pipeline, this will match GitHub PRs.
    stage('Detect changes') {
      when { changeRequest() }
      steps {
        script {
          // Ensure we can diff against main
          sh 'git fetch --no-tags origin main --quiet'

          def base = sh(returnStdout: true,
                        script: 'git merge-base origin/main HEAD').trim()

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
              echo \"Jenkins connected. Services: ${env.SVC_LIST}\";
              exit 0
            '
          """
        }
      }
    }
  }

  post {
    success { echo '✅ Done. (Detected + SSH OK)' }
    failure { echo '❌ Pipeline failed.' }
  }
}
