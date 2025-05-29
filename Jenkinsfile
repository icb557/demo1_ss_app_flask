pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = "flask-demo-${env.BUILD_NUMBER}"
        DOCKER_BUILDKIT = "1"
    }
    
    stages {
        stage('Cleanup') {
            steps {
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
            }
        }
        
        stage('Build') {
            steps {
                script {
                    sh '''
                        echo "=== Building Docker images ==="
                        docker-compose -f docker-compose.yml build --no-cache
                    '''
                }
            }
        }
        
        stage('Test App Import') {
            steps {
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
                }
            }
        }
        
        stage('Health Check') {
            steps {
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
                }
            }
        }
    }
    
    post {
        always {
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
            }
        }
    }
}