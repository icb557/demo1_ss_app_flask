pipeline {
    agent any
    
    stages {
        stage('Build and Run') {
            steps {
                sh '''
                    docker-compose down --volumes --remove-orphans || true
                    docker-compose up --build -d
                    sleep 15
                    docker-compose ps
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}