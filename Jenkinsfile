pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'life-organizer'
        // Define las variables de entorno que irían en tu .env
        DB_USER = credentials('DB_USER')
        DB_PASSWORD = credentials('DB_PASSWORD')
        DB_HOST = 'db'
        DB_PORT = '5432'
        DB_NAME = 'life_organizer'
        FLASK_APP = 'app'
        FLASK_ENV = 'production'  // Cambiado de development a production para entornos CI/CD
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Create .env file') {
            steps {
                sh '''
                    echo "Creating .env file..."
                    cat > .env <<EOF
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
FLASK_APP=${FLASK_APP}
FLASK_ENV=${FLASK_ENV}
EOF
                    chmod 600 .env
                    echo "Generated .env file contents:"
                    cat .env | sed 's/DB_PASSWORD=.*/DB_PASSWORD=*****/'  # Muestra el .env sin exponer la contraseña
                '''
            }
        }
        
        stage('Stop Previous Containers') {
            steps {
                sh '''
                    docker-compose down --remove-orphans || true
                    docker system prune -f || true
                '''
            }
        }
        
        stage('Build and Deploy') {
            steps {
                sh '''
                    docker-compose build --no-cache
                    docker-compose up -d
                '''
            }
        }
        
        stage('Wait for Services') {
            steps {
                sh '''
                    echo "Waiting for services to start..."
                    # Espera inteligente usando healthcheck
                    timeout 60s bash -c '
                        while ! docker-compose ps | grep -q "healthy"; do
                            echo "Waiting for healthy containers..."
                            sleep 5
                        done
                    ' || echo "Warning: Some services may not be fully healthy"
                    
                    # Check if containers are running
                    docker-compose ps
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    # Check if services are running
                    if docker-compose ps web | grep -q "Up"; then
                        echo "✓ Web service is running"
                        # Test actual endpoint
                        if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health | grep -q "200"; then
                            echo "✓ Web service health check passed"
                        else
                            echo "✗ Web service health check failed"
                            docker-compose logs web
                            exit 1
                        fi
                    else
                        echo "✗ Web service failed"
                        docker-compose logs web
                        exit 1
                    fi
                    
                    if docker-compose ps db | grep -q "Up"; then
                        echo "✓ Database service is running"
                        # Test database connection
                        if docker-compose exec db pg_isready -U ${DB_USER} -d ${DB_NAME}; then
                            echo "✓ Database connection successful"
                        else
                            echo "✗ Database connection failed"
                            docker-compose logs db
                            exit 1
                        fi
                    else
                        echo "✗ Database service failed"
                        docker-compose logs db
                        exit 1
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                echo "=== Final container status ==="
                docker-compose ps
                echo "=== Cleanup ==="
                docker-compose down --remove-orphans || true
            '''
            cleanWs()
        }
        failure {
            sh '''
                echo "=== Container Logs ==="
                docker-compose logs
            '''
            archiveArtifacts artifacts: 'docker-compose.log', allowEmptyArchive: true
        }
        success {
            echo '✓ Deployment successful! Application running on http://localhost:5000'
        }
    }
}