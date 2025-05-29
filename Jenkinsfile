pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = 'life-organizer'
        
        // Credenciales desde Jenkins
        DB_USER = 'postgres'
        DB_PASSWORD = 'postgres'
        SECRET_KEY = '68f3b753083b31ee03779bc7b58dfd40d5ae86d570828cc79f33c0dd9fb85261'
        
        // Configuración
        DB_NAME = 'life_organizer'
        FLASK_APP = 'app/__init__.py'
        FLASK_ENV = 'production'
    }
    
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        
        stage('Build') {
            steps {
                sh '''
                    docker-compose down --volumes --remove-orphans || true
                    docker-compose build --no-cache
                '''
            }
        }
        
        stage('Migrate') {
            steps {
                sh '''
                    docker-compose run --rm web flask db upgrade
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    docker-compose up -d
                    sleep 15
                '''
            }
        }
        
        stage('Verify') {
            steps {
                sh '''
                    # Verificar servicios
                    docker-compose ps | grep "Up"
                    
                    # Verificar login manager
                    docker-compose exec web flask shell -c "
                        from app import login_manager
                        print('✓ Login manager configured:', login_manager.login_view)
                    "
                    
                    # Verificar blueprints
                    docker-compose exec web flask routes
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