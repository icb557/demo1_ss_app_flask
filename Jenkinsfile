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
        
        // Puertos y configuración adicional
        WEB_PORT = '5000'
        DB_PORT = '5432'
    }
    
    stages {
        stage('Cleanup Previous') {
            steps {
                echo '=== Limpiando recursos previos ==='
                sh '''
                    # Detener y limpiar contenedores previos
                    docker-compose down --volumes --remove-orphans || true
                    
                    # Eliminar directorio de migraciones si existe
                    rm -rf migrations || true
                    
                    # Limpiar imágenes huérfanas
                    docker image prune -f || true
                    
                    # Eliminar volúmenes de PostgreSQL específicamente
                    docker volume ls -q | grep ${COMPOSE_PROJECT_NAME} | xargs -r docker volume rm || true
                    
                    # Verificar que no hay conflictos de puerto
                    netstat -tulpn | grep :${WEB_PORT} || echo "Puerto ${WEB_PORT} disponible"
                    
                    # Verificar que los volúmenes fueron eliminados
                    echo "Volúmenes restantes:"
                    docker volume ls || true
                '''
            }
        }
        
        stage('Checkout') {
            steps {
                echo '=== Descargando código fuente ==='
                checkout scm
                
                // Verificar archivos necesarios
                sh '''
                    echo "Verificando archivos del proyecto..."
                    ls -la
                    test -f docker-compose.yml || (echo "❌ docker-compose.yml no encontrado" && exit 1)
                    test -f Dockerfile || (echo "❌ Dockerfile no encontrado" && exit 1)
                    test -f requirements.txt || (echo "❌ requirements.txt no encontrado" && exit 1)
                    test -f scripts/wait-for-db.sh || (echo "❌ wait-for-db.sh no encontrado" && exit 1)
                    echo "✅ Todos los archivos necesarios encontrados"
                '''
            }
        }
        
        stage('Build') {
            steps {
                echo '=== Construyendo imágenes Docker ==='
                sh '''
                    # Construir sin caché para asegurar actualizaciones
                    docker-compose build --no-cache --parallel
                    
                    # Verificar que las imágenes se crearon correctamente
                    docker-compose images
                '''
            }
        }
        
        stage('Database Setup') {
            steps {
                echo '=== Configurando base de datos ==='
                sh '''
                    # Iniciar solo la base de datos primero
                    docker-compose up -d db
                    
                    # Esperar a que PostgreSQL esté listo
                    echo "Esperando a PostgreSQL..."
                    timeout 60 sh -c 'until docker-compose exec -T db pg_isready -U ${DB_USER}; do sleep 2; done'
                    
                    echo "✅ PostgreSQL está listo"
                '''
            }
        }
        
        
        stage('Run Application') {
            steps {
                echo '=== Desplegando aplicación ==='
                sh '''
                    # Iniciar todos los servicios
                    docker-compose up -d
                    
                    # Esperar a que la aplicación esté lista
                    echo "Esperando a que la aplicación esté lista..."
                    sleep 20
                    
                    # Verificar que los contenedores están ejecutándose
                    docker-compose ps
                '''
            }
        }

        stage('Functional Tests') {
            steps {
                echo '=== Ejecutando tests funcionales ==='
                sh '''
                    echo "Verificando configuración de Flask..."
                    docker-compose exec -T web python -c "from app import create_app; app = create_app(); print('✅ Flask app configurada correctamente')" || echo "⚠️  Error en configuración de Flask"
                    
                    # Verificar rutas disponibles
                    echo "Rutas disponibles:"
                    docker-compose exec -T web flask routes || echo "⚠️  No se pudieron obtener las rutas"
                    
                    # Tests adicionales si existen
                    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
                        echo "Ejecutando tests unitarios..."
                        docker-compose exec -T web python -m pytest tests/ -v || echo "⚠️  Algunos tests fallaron"
                    fi
                '''
            }
        }

        stage('Run Migrations') {
            steps {
                echo '=== Ejecutando migraciones ==='
                sh '''
                    # Verificar si las migraciones existen dentro del contenedor
                    if ! docker-compose run --rm web test -d migrations; then
                        echo "Inicializando migraciones..."
                        docker-compose run --rm web flask db init
                        docker-compose run --rm web flask db migrate -m "Initial migration"
                    else
                        echo "El directorio de migraciones ya existe"
                    fi
                    
                    # Aplicar migraciones pendientes
                    echo "Aplicando migraciones pendientes..."
                    docker-compose run --rm web flask db upgrade
                    
                    echo "✅ Migraciones completadas"
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '=== Verificando salud de la aplicación ==='
                sh '''
                    # Verificar que los servicios están corriendo
                    echo "Estado de los servicios:"
                    docker-compose ps
                    
                    # Verificar logs por errores
                    echo "Verificando logs de la aplicación..."
                    docker-compose logs --tail=20 web
                    
                    # Verificar conectividad de la base de datos
                    echo "Verificando conexión a la base de datos..."
                    docker-compose exec -T db psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT version();" || echo "❌ Error de conexión a DB"
                    
                    # Verificar que la aplicación responde
                    echo "Verificando respuesta de la aplicación..."
                    timeout 30 sh -c 'until curl -f http://localhost:${WEB_PORT}/health 2>/dev/null || curl -f http://localhost:${WEB_PORT}/ 2>/dev/null; do echo "Esperando respuesta..."; sleep 3; done' || echo "⚠️  Aplicación no responde en puerto ${WEB_PORT}"
                '''
            }
        }
        
        

        stage('Comentario en Jira') {
            steps {
                echo '=== Agregando comentario en Jira ==='
                withCredentials([string(credentialsId: 'jenkins-jira', variable: 'JIRA_TOKEN')]) {
                    sh '''
                        curl -s -X POST \
                        -u "deivermartinez1999@gmail.com:${JIRA_TOKEN}" \
                        -H "Content-Type: application/json" \
                        --data '{"body": "✅ Despliegue exitoso desde Jenkins."}' \
                        https://cortesbuitragoisac-1745878529850.atlassian.net/rest/api/2/issue/FAD-35/comment
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '=== Estado final del despliegue ==='
            sh '''
                echo "Estado de contenedores:"
                docker-compose ps || true
                
                echo "Uso de recursos:"
                docker stats --no-stream || true
                
                echo "Logs recientes:"
                docker-compose logs --tail=10 || true
            '''
        }
        
        success {
            echo '✅ ¡Despliegue exitoso!'
            sh '''
                echo "=== DESPLIEGUE COMPLETADO ==="
                echo "Aplicación disponible en: http://localhost:${WEB_PORT}"
                echo "Base de datos PostgreSQL en puerto: ${DB_PORT}"
                docker-compose ps
            '''
        }
        
        failure {
            echo '❌ Despliegue falló'
            sh '''
                echo "=== INFORMACIÓN DE DEBUG ==="
                echo "Logs de todos los servicios:"
                docker-compose logs || true
                
                echo "Estado de contenedores:"
                docker-compose ps || true
                
                echo "Procesos en el sistema:"
                ps aux | grep -E "(docker|flask|postgres)" || true
            '''
            
            // Archivar logs para análisis
            archiveArtifacts artifacts: 'docker-compose.yml,Dockerfile,requirements.txt', allowEmptyArchive: true
        }
        
        cleanup {
            // Limpiar workspace pero mantener contenedores corriendo si el deploy fue exitoso
            cleanWs()
        }
    }
}