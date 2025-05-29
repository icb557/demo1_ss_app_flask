pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'life_organizer_${BUILD_NUMBER}'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Construir servicios') {
            steps {
                sh 'docker-compose -p ${COMPOSE_PROJECT_NAME} build'
            }
        }

        stage('Levantar servicios') {
            steps {
                sh 'docker-compose -p ${COMPOSE_PROJECT_NAME} up -d'
                sh 'sleep 10'  // Espera a que los servicios estén listos
            }
        }

        stage('Verificar') {
            steps {
                sh '''
                    docker-compose -p ${COMPOSE_PROJECT_NAME} exec web flask check
                    docker-compose -p ${COMPOSE_PROJECT_NAME} exec web python -m pytest
                '''
            }
        }
    }

    post {
        always {
            sh 'docker-compose -p ${COMPOSE_PROJECT_NAME} down -v'
            cleanWs()
        }
    }
}