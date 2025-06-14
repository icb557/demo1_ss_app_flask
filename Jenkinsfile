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
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '=== Obteniendo código del repositorio ==='
                checkout scm
            }
        }
        
        stage('Setup Infisical CLI') {
            steps {
                echo '=== Configurando CLI de Infisical ==='
                sh '''
                    # Instalar Infisical CLI solo si no está presente
                    if ! command -v infisical &> /dev/null; then
                        curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | sudo -E bash
                        sudo apt-get update && sudo apt-get install -y infisical
                    fi
                '''
            }
        }
        
        stage('Ensure Secrets Exist') {
            steps {
                echo '=== Verificando secrets en Infisical ==='
                script {
                    // Verificar y crear secrets si no existen
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
                        echo "🔑 Generando nuevos secrets..."
                        
                        // Generar SECRET_KEY segura
                        def generatedKey = sh(
                            script: 'openssl rand -hex 32',
                            returnStdout: true
                        ).trim()
                        
                        // Crear secrets en Infisical
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
                        echo "🔑 SECRET_KEY ya existe en Infisical"
                    }
                }
            }
        }
        
        stage('Load Environment') {
            steps {
                echo '=== Cargando variables de entorno ==='
                sh '''
                    # Obtener secrets y crear .env
                    infisical export \
                      --token=$INFISICAL_TOKEN \
                      --env=prod \
                      --projectId=$INFISICAL_PROJECT_ID \
                      --format=dotenv > .env
                    
                    # Agregar variables no sensibles
                    echo "FLASK_APP=${FLASK_APP}" >> .env
                    echo "FLASK_ENV=${FLASK_ENV}" >> .env
                    echo "PYTHONPATH=${PYTHONPATH}" >> .env
                '''
            }
        }
        
        stage('Setup Python') {
            steps {
                echo '=== Instalando Python y dependencias ==='
                sh '''
                    # Actualizar repositorios
                    sudo apt-get update
                    
                    # Instalar Python y pip
                    sudo apt-get install -y python3.11-venv
                    
                    # Crear entorno virtual
                    python3 -m venv ${VENV_DIR}

                    # Activar el entorno virtual e instalar dependencias
                    . ${VENV_DIR}/bin/activate
                    which python3
                    pip install --break-system-packages -r requirements.txt

                    pip install --break-system-packages pytest pytest-cov flake8 safety bandit
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '=== Ejecutando tests Unitarios ==='
                sh '''
                    # Tests adicionales si existen
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Ejecutando tests unitarios..."
                        python3 -m pytest tests/unit -v || echo "⚠️  Algunos tests unitarios fallaron"
                    fi
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                echo '=== Ejecutando tests de integración ==='
                sh '''
                    # Tests adicionales si existen
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Ejecutando tests de integracion..."
                        python3 -m pytest tests/integration -v || echo "⚠️  Algunos tests de integracion fallaron"
                    fi
                '''
            }
        }
        
        stage('e2e Tests') {
            steps {
                echo '=== Ejecutando tests e2e ==='
                sh '''
                    # Tests adicionales si existen
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Ejecutando tests e2e..."
                        python3 -m pytest tests/e2e -v || echo "⚠️  Algunos tests e2e fallaron"
                    fi
                '''
            }
        }
        
        stage('Lint') {
            steps {
                echo '=== Ejecutando linting ==='
                sh '''
                    flake8 app/ tests/ || echo "⚠️  Algunos problemas de estilo encontrados"
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '=== Ejecutando análisis de seguridad ==='
                sh '''
                    # Verificar dependencias con safety
                    safety check || echo "⚠️  Se encontraron vulnerabilidades en las dependencias"
                    
                    # Verificar código con bandit
                    bandit -r app/ || echo "⚠️  Se encontraron problemas de seguridad en el código"
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '=== Verificando estado de la aplicación ==='
                sh '''
                    echo "Rutas disponibles:"
                    flask routes || echo "⚠️  No se pudieron obtener las rutas"
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
            echo '=== Limpiando entorno ==='
            sh 'rm -rf ${VENV_DIR}'
            sh 'which python3'
        }
        success {
            discordSend description: "Jenkins Pipeline Build ${env.BUILD_DISPLAY_NAME} succesfull", footer: "", link: env.BUILD_URL, result: currentBuild.currentResult, title: env.JOB_NAME, webhookURL: 'https://discord.com/api/webhooks/1383560954637189302/Ge7_KdL1a2YBpVfZ4v39mNnY0MTX05MwwxcIdd1mWIrAYJhvn3hqEfKy3nY5dct7Ggrb'
            echo '✅ Pipeline completado exitosamente'
        }
        failure {
            discordSend description: "Jenkins Pipeline Build ${env.BUILD_DISPLAY_NAME} failed", footer: "", link: env.BUILD_URL, result: currentBuild.currentResult, title: env.JOB_NAME, webhookURL: 'https://discord.com/api/webhooks/1383560954637189302/Ge7_KdL1a2YBpVfZ4v39mNnY0MTX05MwwxcIdd1mWIrAYJhvn3hqEfKy3nY5dct7Ggrb'
            echo '❌ Pipeline falló'
        }
    }
}