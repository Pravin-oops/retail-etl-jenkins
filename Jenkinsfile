pipeline {
    agent any

    // 1. SCHEDULE: Run at 9:00 AM IST daily
    // Cron Syntax: Minute Hour Day Month DayOfWeek
    // TZ=Asia/Kolkata ensures it follows Indian Standard Time
    triggers {
        cron('TZ=Asia/Kolkata 0 9 * * *') 
    }

    environment {
        // Ensure Python knows where to find libraries
        PATH = "/opt/venv/bin:$PATH"
    }

    stages {
        stage('Checkout') {
            steps {
                // Get the latest code from the workspace
                checkout scm
            }
        }

        stage('1. Generate Data') {
            steps {
                script {
                    echo "--- Generating Data for ${new Date()} ---"
                    // Runs the V2 script you built earlier
                    sh 'python3 script/generate_data.py'
                }
            }
        }

        stage('2. Run ETL') {
            steps {
                script {
                    echo "--- Triggering Oracle PL/SQL ---"
                    // Runs the new Python Trigger we just made
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