pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'life-organizer'
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        echo "=== Environment Setup ==="
                        echo "Current user: $(whoami)"
                        echo "Working directory: $(pwd)"

                        if ! command -v docker-compose &> /dev/null; then
                            echo "Installing Docker Compose..."
                            curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
                            chmod +x /usr/local/bin/docker-compose
                            ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
                        fi

                        chmod 666 /var/run/docker.sock || echo "Could not change socket permissions"

                        echo "Testing Docker access..."
                        docker version || echo "Docker not accessible"
                    '''
                }
            }
        }

        stage('Checkout') {
            steps {
                echo "Code already checked out by SCM"
                sh '''
                    ls -la
                    if [ -f "docker-compose.yml" ]; then
                        cat docker-compose.yml
                    fi
                '''
            }
        }

        stage('Stop Previous Containers') {
            steps {
                script {
                    sh '''
                        docker-compose down --remove-orphans 2>/dev/null || echo "No previous containers to stop"
                        docker stop $(docker ps -q) 2>/dev/null || echo "No containers to stop"
                        docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"
                    '''
                }
            }
        }

        stage('Build and Deploy') {
            steps {
                script {
                    sh '''
                        echo "Building and starting services..."
                        docker-compose up -d --build
                        sleep 10
                    '''
                }
            }
        }

        stage('Run Migrations') {
            steps {
                script {
                    sh '''
                        echo "Running Flask database migrations..."

                        # Esperar a que la base de datos esté lista
                        docker-compose exec web /usr/local/bin/wait-for-db.sh db

                        # Ejecutar migraciones aunque el directorio ya exista
                        docker-compose exec web flask db migrate -m "auto migration" || echo "No changes detected"
                        docker-compose exec web flask db upgrade
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    sh '''
                        docker-compose ps

                        if docker-compose ps | grep -q "Up"; then
                            echo "✅ Services are running"
                        else
                            echo "❌ Services are not running properly"
                            docker-compose logs
                            exit 1
                        fi

                        echo "Testing web endpoint..."
                        for i in {1..5}; do
                            if curl -f -s http://localhost:5000; then
                                echo "✅ Web service is responding"
                                break
                            else
                                echo "Attempt $i: Waiting for web service..."
                                sleep 5
                            fi
                        done
                    '''
                }
            }
        }

        stage('Show Results') {
            steps {
                sh '''
                    echo "=== Deployment Results ==="
                    docker-compose ps
                    docker-compose logs --tail=10
                    df -h
                    free -h
                '''
            }
        }
    }

    post {
        always {
            script {
                sh '''
                    echo "=== Final Status ==="
                    docker-compose ps || echo "Could not get container status"
                    ls -la /var/run/docker.sock
                '''
            }
        }
        failure {
            script {
                sh '''
                    echo "=== FAILURE DEBUG INFO ==="
                    docker --version || echo "Docker not working"
                    docker-compose logs || echo "Could not get logs"
                    docker-compose down || echo "Could not stop containers"
                '''
            }
        }
        success {
            echo '''
            🎉 Pipeline completed successfully!

            Application should be available at:
            http://localhost:5000

            Commands to manage the deployment:
            - docker-compose ps
            - docker-compose logs
            - docker-compose down
            '''
        }
    }
}
