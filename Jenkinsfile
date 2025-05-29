pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'flask-demo'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Descargando código del repositorio...'
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo 'Construyendo la aplicación Flask con Docker...'
                script {
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down || true'
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} build'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Levantando la aplicación Flask...'
                script {
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} up -d'
                    sleep 15
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} ps'
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Verificando que la aplicación esté funcionando...'
                script {
                    sh '''
                        for i in {1..10}; do
                            if curl -f http://localhost:5000 > /dev/null 2>&1; then
                                echo "✅ Aplicación Flask funcionando correctamente"
                                exit 0
                            fi
                            echo "Intento $i/10 - Esperando..."
                            sleep 5
                        done
                        echo "❌ La aplicación no responde"
                        exit 1
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '🎉 Pipeline exitoso - App disponible en http://localhost:5000'
        }
        failure {
            echo '❌ Pipeline falló'
            sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=50 || true'
        }
    }
}