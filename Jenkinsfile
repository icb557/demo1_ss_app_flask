pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'life-organizer'
        DB_USER = 'postgres'
        DB_PASSWORD = 'postgres'
        DB_HOST = 'db'
        DB_PORT = '5432'
        DB_NAME = 'life_organizer'
        FLASK_APP = 'app.py'
        FLASK_ENV = 'production'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
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
                '''
            }
        }
        
        stage('Build and Deploy') {
            steps {
                sh '''
                    docker-compose down --volumes --remove-orphans || true
                    docker-compose build --no-cache
                    docker-compose up -d
                    
                    # Espera para migraciones
                    echo "Waiting for migrations to complete..."
                    sleep 15
                    
                    # Verifica migraciones
                    if docker-compose exec web flask db current | grep -q "(head)"; then
                        echo "✓ Migrations applied successfully"
                    else
                        echo "✗ Migrations failed"
                        docker-compose logs web
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    # Verificación de servicios
                    if docker-compose ps web | grep -q "Up"; then
                        echo "✓ Web service running"
                        # Verificación de endpoint
                        if curl -s http://localhost:5000/health | grep -q "healthy"; then
                            echo "✓ Health check passed"
                        else
                            echo "✗ Health check failed"
                            exit 1
                        fi
                    else
                        echo "✗ Web service not running"
                        exit 1
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose ps'
            cleanWs()
        }
        failure {
            archiveArtifacts artifacts: 'docker-compose.log', allowEmptyArchive: true
        }
    }
}