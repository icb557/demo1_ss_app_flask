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
                    sleep 30
                    
                    # Check if containers are running
                    docker-compose ps
                    
                    # Wait a bit more for full initialization
                    sleep 15
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    # Check if services are running
                    if docker-compose ps web | grep -q "Up"; then
                        echo "✓ Web service is running"
                    else
                        echo "✗ Web service failed"
                        docker-compose logs web
                        exit 1
                    fi
                    
                    if docker-compose ps db | grep -q "Up"; then
                        echo "✓ Database service is running"
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
            sh 'docker-compose ps'
        }
        failure {
            sh '''
                echo "=== Container Logs ==="
                docker-compose logs
                docker-compose down --remove-orphans
            '''
        }
        success {
            echo '✓ Deployment successful! Application running on http://localhost:5000'
        }
    }
}