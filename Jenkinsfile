pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'flask-demo'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        HEALTH_CHECK_ENDPOINT = '/healthcheck'  // Endpoint específico para health checks
        MAX_RETRIES = 10                       // Intentos máximos para health check
        RETRY_DELAY = 5                        // Segundos entre intentos
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔍 Descargando código del repositorio...'
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],  // Cambia según tu rama principal
                    extensions: [[$class: 'CleanBeforeCheckout']],  // Limpiar workspace
                    userRemoteConfigs: [[url: 'https://github.com/tu-usuario/tu-repo.git']]
                ])
            }
        }
        
        stage('Build') {
            steps {
                echo '🏗️ Construyendo la aplicación Flask con Docker...'
                script {
                    // Limpiar containers previos
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down --remove-orphans || true'
                    
                    // Construir con cache pero forzar rebuild de dependencias
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} build --no-cache --pull'
                    
                    // Limpiar imágenes huérfanas
                    sh 'docker image prune -f'
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Ejecutando tests...'
                script {
                    try {
                        // Ejecutar tests y guardar reporte
                        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} run --rm web pytest --junitxml=test-results.xml'
                        junit 'test-results.xml'  // Reporte de tests en Jenkins
                    } finally {
                        // Limpiar después de tests
                        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down'
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo '🚀 Desplegando la aplicación Flask...'
                script {
                    // Levantar servicios en modo detached
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} up -d --force-recreate'
                    
                    // Verificar estado de los servicios
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} ps'
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=20'
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo '🏥 Verificando salud de la aplicación...'
                script {
                    def healthy = false
                    
                    for (int i = 1; i <= MAX_RETRIES; i++) {
                        try {
                            // Usar curl con timeout y seguimiento de redirecciones
                            sh """
                                curl -fsS --max-time 5 --retry 3 \
                                http://localhost:5000${HEALTH_CHECK_ENDPOINT} | grep -q '"status":"healthy"'
                            """
                            healthy = true
                            echo "✅ Health check exitoso en intento ${i}"
                            break
                        } catch (Exception e) {
                            echo "⏳ Intento ${i}/${MAX_RETRIES} - Esperando ${RETRY_DELAY} segundos..."
                            sleep RETRY_DELAY
                        }
                    }
                    
                    if (!healthy) {
                        // Obtener logs antes de fallar
                        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=100'
                        error('❌ Health check fallido después de ${MAX_RETRIES} intentos')
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Limpiando recursos temporales...'
            script {
                // Guardar logs para diagnóstico
                sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} logs --no-color > docker-compose.log'
                archiveArtifacts artifacts: 'docker-compose.log', allowEmptyArchive: true
                
                // Detener containers pero mantener volúmenes
                sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down || true'
            }
        }
        success {
            echo '🎉 Pipeline completado exitosamente!'
            // Opcional: Notificación por Slack/Email
            // slackSend color: 'good', message: "Pipeline ${env.BUILD_NUMBER} exitoso"
        }
        failure {
            echo '❌ Pipeline falló'
            script {
                // Logs detallados para diagnóstico
                sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=100 || true'
                sh 'docker ps -a || true'
                sh 'docker network ls || true'
            }
        }
    }
}