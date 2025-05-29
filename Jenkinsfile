pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'life-organizer'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Stop Previous Containers') {
            steps {
                script {
                    sh '''
                        # Try both docker-compose and docker compose commands
                        (docker-compose down --remove-orphans 2>/dev/null || docker compose down --remove-orphans 2>/dev/null || echo "No previous containers to stop")
                        docker system prune -f || true
                    '''
                }
            }
        }
        
        stage('Build and Deploy') {
            steps {
                script {
                    sh '''
                        # Try both docker-compose and docker compose commands
                        if command -v docker-compose >/dev/null 2>&1; then
                            docker-compose build --no-cache
                            docker-compose up -d
                        elif docker compose version >/dev/null 2>&1; then
                            docker compose build --no-cache
                            docker compose up -d
                        else
                            echo "Neither docker-compose nor docker compose found!"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        echo "Waiting for services to be ready..."
                        sleep 30
                        
                        # Check if web service is running
                        if (docker-compose ps web 2>/dev/null || docker compose ps web 2>/dev/null) | grep -q "Up"; then
                            echo "Web service is running"
                        else
                            echo "Web service failed to start"
                            exit 1
                        fi
                        
                        # Check if db service is running
                        if (docker-compose ps db 2>/dev/null || docker compose ps db 2>/dev/null) | grep -q "Up"; then
                            echo "Database service is running"
                        else
                            echo "Database service failed to start"
                            exit 1
                        fi
                        
                        # Optional: Test web endpoint
                        curl -f http://localhost:5000 || echo "Web service not responding yet"
                    '''
                }
            }
        }
        
        stage('Show Running Services') {
            steps {
                sh '''
                    echo "=== Running Containers ==="
                    docker-compose ps
                    echo "=== Container Logs ==="
                    docker-compose logs --tail=20
                '''
            }
        }
    }
    
    post {
        always {
            script {
                sh '''
                    echo "=== Final Container Status ==="
                    docker-compose ps
                '''
            }
        }
        failure {
            script {
                sh '''
                    echo "=== Error Logs ==="
                    docker-compose logs
                    echo "=== Cleaning up failed deployment ==="
                    docker-compose down --remove-orphans
                '''
            }
        }
        success {
            echo 'Deployment successful! Application is running on http://localhost:5000'
        }
    }
}