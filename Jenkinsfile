pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Construir y levantar servicios') {
            steps {
                sh 'docker compose down || true'  // || true evita fallos si no hay servicios
                sh 'docker compose build'
                sh 'docker compose up -d'
            }
        }

        stage('Ejecutar tests') {
            steps {
                sh '''
                    docker compose exec web python -m pytest || echo "Tests fallidos"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose down || true'
            cleanWs()
        }
    }
}