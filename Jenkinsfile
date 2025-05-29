pipeline {
    agent any
    
    environment {
<<<<<<< HEAD
        COMPOSE_PROJECT_NAME = 'flask-demo'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        HEALTH_CHECK_ENDPOINT = '/healthcheck'  // Endpoint específico para health checks
        MAX_RETRIES = 10                       // Intentos máximos para health check
        RETRY_DELAY = 5                        // Segundos entre intentos
=======
        COMPOSE_PROJECT_NAME = "flask-demo-${env.BUILD_NUMBER}"
        DOCKER_BUILDKIT = "1"
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
    }
    
    stages {
        stage('Cleanup') {
            steps {
<<<<<<< HEAD
                echo '🔍 Descargando código del repositorio...'
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],  // Cambia según tu rama principal
                    extensions: [[$class: 'CleanBeforeCheckout']],  // Limpiar workspace
                    userRemoteConfigs: [[url: 'https://github.com/tu-usuario/tu-repo.git']]
                ])
=======
                script {
                    // Limpiar contenedores previos
                    sh '''
                        docker-compose -f docker-compose.yml down --volumes --remove-orphans || true
                        docker system prune -f || true
                    '''
                }
            }
        }
        
        stage('Verify Files') {
            steps {
                sh '''
                    echo "=== Project Structure ==="
                    ls -la
                    echo "=== Checking app.py ==="
                    if [ -f "app.py" ]; then
                        echo "app.py exists"
                        head -10 app.py
                    else
                        echo "ERROR: app.py not found!"
                        exit 1
                    fi
                    echo "=== Checking requirements.txt ==="
                    if [ -f "requirements.txt" ]; then
                        echo "requirements.txt exists"
                        cat requirements.txt
                    else
                        echo "ERROR: requirements.txt not found!"
                        exit 1
                    fi
                '''
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
            }
        }
        
        stage('Build') {
            steps {
<<<<<<< HEAD
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
=======
                script {
                    sh '''
                        echo "=== Building Docker images ==="
                        docker-compose -f docker-compose.yml build --no-cache
                    '''
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
                }
            }
        }
        
        stage('Test App Import') {
            steps {
<<<<<<< HEAD
                echo '🚀 Desplegando la aplicación Flask...'
                script {
                    // Levantar servicios en modo detached
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} up -d --force-recreate'
                    
                    // Verificar estado de los servicios
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} ps'
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=20'
=======
                script {
                    sh '''
                        echo "=== Testing Flask app import ==="
                        docker-compose -f docker-compose.yml run --rm web python -c "
import sys
print('Python path:', sys.path)
try:
    import app
    print('✓ App imported successfully')
    print('✓ Flask app found:', hasattr(app, 'app'))
except ImportError as e:
    print('✗ Import error:', e)
    import os
    print('Current directory:', os.getcwd())
    print('Directory contents:', os.listdir('.'))
    sys.exit(1)
"
                    '''
                }
            }
        }
        
        stage('Start Services') {
            steps {
                script {
                    sh '''
                        echo "=== Starting services ==="
                        docker-compose -f docker-compose.yml up -d
                        
                        echo "=== Waiting for services ==="
                        sleep 30
                        
                        echo "=== Checking service status ==="
                        docker-compose -f docker-compose.yml ps
                    '''
                }
            }
        }
        
        stage('Check Logs') {
            steps {
                script {
                    sh '''
                        echo "=== Application Logs ==="
                        docker-compose -f docker-compose.yml logs --tail=50
                    '''
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
                }
            }
        }
        
        stage('Health Check') {
            steps {
<<<<<<< HEAD
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
=======
                script {
                    sh '''
                        echo "=== Health Check ==="
                        # Esperar a que la aplicación esté lista
                        for i in {1..10}; do
                            if curl -f http://localhost:5000 2>/dev/null; then
                                echo "✓ Application is responding"
                                break
                            else
                                echo "Attempt $i: Application not ready, waiting..."
                                sleep 10
                            fi
                        done
                    '''
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
                }
            }
        }
    }
    
    post {
        always {
<<<<<<< HEAD
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
=======
            script {
                sh '''
                    echo "=== Final Logs ==="
                    docker-compose -f docker-compose.yml logs --tail=100
                    
                    echo "=== Cleanup ==="
                    docker-compose -f docker-compose.yml down --volumes
                '''
            }
        }
        failure {
            script {
                sh '''
                    echo "=== Debugging Information ==="
                    docker-compose -f docker-compose.yml ps
                    docker images
                    docker-compose -f docker-compose.yml logs
                '''
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
            }
        }
    }
}