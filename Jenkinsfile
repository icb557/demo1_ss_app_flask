pipeline {
    agent any
    
    environment {
        // Variables de entorno
        DB_NAME = 'life_organizer'
        WEB_PORT = '5000'
        FLASK_APP = 'app/__init__.py'
        FLASK_ENV = 'testing'
        PYTHONPATH = "${WORKSPACE}"
        VENV_DIR = "venv"
        INFISICAL_TOKEN = credentials('infisical-token-id')
        INFISICAL_PROJECT_ID = '61d5b470-4cf8-4db4-8e18-0f73705f6d21'
        DB_USER = 'postgres'
        DB_PASSWORD = 'postgres'
        DB_PORT = '5432'
        DISCORD_WEBHOOK= credentials('discord-webhook')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '=== Getting source code from repository ==='
                checkout scm
            }
        }
        
        stage('Setup Infisical CLI') {
            steps {
                echo '=== Setting CLI of Infisical ==='
                sh '''
                    # Install Infisical CLI if not installed
                    if ! command -v infisical &> /dev/null; then
                        curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | sudo -E bash
                        sudo apt-get update && sudo apt-get install -y infisical
                    fi
                '''
            }
        }
        
        stage('Ensure Secrets Exist') {
            steps {
                echo '=== Verifying secrets in Infisical ==='
                script {
                    def secretKeyExists = sh(
                        script: """
                            infisical get SECRET_KEY \
                              --token=${INFISICAL_TOKEN} \
                              --env=prod \
                              --projectId=${INFISICAL_PROJECT_ID} >/dev/null 2>&1 && echo "true" || echo "false"
                        """,
                        returnStdout: true
                    ).trim()
                    
                    if (secretKeyExists == "false") {
                        echo "🔑 Generating new secrets..."
                        
                        def generatedKey = sh(
                            script: 'openssl rand -hex 32',
                            returnStdout: true
                        ).trim()
                        
                        sh """
                            infisical secrets set SECRET_KEY="${generatedKey}" \
                            --env=prod \
                            --projectId=${INFISICAL_PROJECT_ID} \
                            --token=${INFISICAL_TOKEN}

                            infisical secrets set DB_USER="${DB_USER}" \
                            --env=prod \
                            --projectId=${INFISICAL_PROJECT_ID} \
                            --token=${INFISICAL_TOKEN}

                            infisical secrets set DB_PASSWORD="${DB_PASSWORD}" \
                            --env=prod \
                            --projectId=${INFISICAL_PROJECT_ID} \
                            --token=${INFISICAL_TOKEN}

                            infisical secrets set DB_PORT="${DB_PORT}" \
                            --env=prod \
                            --projectId=${INFISICAL_PROJECT_ID} \
                            --token=${INFISICAL_TOKEN}

                            infisical secrets set DB_NAME="life_organizer" \
                            --env=prod \
                            --projectId=${INFISICAL_PROJECT_ID} \
                            --token=${INFISICAL_TOKEN}

                            infisical secrets set WEB_PORT="8000" \
                            --env=prod \
                            --projectId=${INFISICAL_PROJECT_ID} \
                            --token=${INFISICAL_TOKEN}
                        """
                    } else {
                        echo "🔑 SECRET_KEY already exists in Infisical"
                    }
                }
            }
        }
        
        stage('Load Environment') {
            steps {
                echo '=== Loading environment variables ==='
                sh '''
                    # Get secrets and create .env
                    infisical export \
                      --token=$INFISICAL_TOKEN \
                      --env=prod \
                      --projectId=$INFISICAL_PROJECT_ID \
                      --format=dotenv > .env
                    
                    # Add non-sensitive variables
                    echo "FLASK_APP=${FLASK_APP}" >> .env
                    echo "FLASK_ENV=${FLASK_ENV}" >> .env
                    echo "PYTHONPATH=${PYTHONPATH}" >> .env
                '''
            }
        }
        
        stage('Setup Python') {
            steps {
                echo '=== Installing Python and dependencies ==='
                sh '''
                    # Update repositories
                    sudo apt-get update
                    
                    # Install Python-env
                    sudo apt-get install -y python3.11-venv
                    
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
                    flake8 app/ tests/ || echo "⚠️ Some linting issues found"
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '=== Running security scan ==='
                sh '''
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
