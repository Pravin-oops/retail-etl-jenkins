pipeline {
    agent any

    // SCHEDULE: 03:30 AM UTC = 09:00 AM IST
    triggers {
        cron('30 3 * * *') 
    }

    environment {
        // Ensure Python knows where to find libraries
        PATH = "/opt/venv/bin:\$PATH"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('1. Generate Data') {
            steps {
                script {
                    echo "--- Generating Data for \${new Date()} ---"
                    sh 'python3 script/generate_data.py'
                }
            }
        }

        stage('2. Run ETL') {
            steps {
                script {
                    echo "--- Triggering Oracle PL/SQL ---"
                    sh 'python3 script/trigger_etl.py'
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline Succeeded!'
        }
        failure {
            echo '❌ Pipeline Failed. Check logs.'
        }
    }
}