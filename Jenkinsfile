pipeline {
    agent any
    
    environment {
        // Variables de entorno
        PYTHONPATH = "${WORKSPACE}"
        VENV_DIR = "venv"
        INFISICAL_TOKEN = credentials('infisical-token-id')
        INFISICAL_PROJECT_ID = '61d5b470-4cf8-4db4-8e18-0f73705f6d21'
        DISCORD_WEBHOOK= credentials('discord-webhook')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '=== Getting source code from repository ==='
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                echo '=== Installing Python and dependencies ==='
                sh '''
                    # Create virtual environment
                    python3 -m venv ${VENV_DIR}

                    # Activate virtual environment and install dependencies
                    . ${VENV_DIR}/bin/activate
                    which python3
                    pip install --break-system-packages -r requirements.txt

                    pip install --break-system-packages pytest pytest-cov flake8 safety bandit
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '=== Run unit tests ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    # Tests adicionales si existen
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Running unit tests..."
                        python3 -m pytest tests/unit -v
                    fi
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                echo '=== Run Integration Tests ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Running Integration test..."
                        python3 -m pytest tests/integration -v
                    fi
                '''
            }
        }
        
        stage('e2e Tests') {
            steps {
                echo '=== Run e2e test ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Running e2e tests..."
                        python3 -m pytest tests/e2e -v
                    fi
                '''
            }
        }
        
        stage('Lint') {
            steps {
                echo '=== Run linting ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 app/ tests/ || echo "⚠️ Some linting issues found"
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '=== Running security scan ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    # Verify dependencies with safety
                    safety check || echo "⚠️ Some security issues found"
                    
                    # Verify code with bandit
                    bandit -r app/ || echo "⚠️ Some security issues found"
                '''
            }
        }
        
        stage('Check routes') {
            steps {
                echo '=== Verify routes ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "Rutas disponibles:"
                    flask routes 
                '''
            }
        }
        
        /* stage('Add comment in Jira') {
            steps {
                echo '=== Agregando comentario en Jira ==='
                script {
                    def commitMessage = env.GIT_COMMIT_MESSAGE
                    def jiraComment = """✅ Pipeline completado exitosamente
🔄 Último commit: ${env.GIT_COMMIT}
👤 Autor: ${env.GIT_AUTHOR_NAME}
📝 Mensaje: ${commitMessage}""".replaceAll('\n', '\\\\n').replace('"', '\\"')

                    echo "Comentario para Jira: ${jiraComment}"

                    withCredentials([
                        string(credentialsId: 'jenkins-jira', variable: 'JIRA_TOKEN'),
                        string(credentialsId: 'jenkins-jira-user', variable: 'JIRA_USER')
                    ]) {
                        def commentJson = """{ "body": "${jiraComment}" }"""
                        def jiraUrl = "https://cortesbuitragoisac-1745878529850.atlassian.net/rest/api/2/issue/FAD-54/comment"

                        echo "Usuario: ${JIRA_USER}"
                        echo "Token: ${JIRA_TOKEN}"

                        sh """
                            curl -s -X POST \\
                            -u "${JIRA_USER}:${JIRA_TOKEN}" \\
                            -H "Content-Type: application/json" \\
                            --data '${commentJson}' \\
                            ${jiraUrl}
                        """
                    }
                }
                
            }
        } */
    }
    
    post {
        always {
            echo '=== Cleaning environment ==='
            sh 'rm -rf ${VENV_DIR}'
            sh 'which python3'
        }
        success {
            discordSend description: "Jenkins Pipeline Build ${env.BUILD_DISPLAY_NAME} succesfull", footer: "", link: env.BUILD_URL, result: currentBuild.currentResult, title: env.JOB_NAME, webhookURL: env.DISCORD_WEBHOOK
            echo '✅ Pipeline finished successfully'
        }
        failure {
            discordSend description: "Jenkins Pipeline Build ${env.BUILD_DISPLAY_NAME} failed", footer: "", link: env.BUILD_URL, result: currentBuild.currentResult, title: env.JOB_NAME, webhookURL: env.DISCORD_WEBHOOK
            echo '❌ Pipeline failed'
        }
    }
}
