pipeline {
    agent any
    stages {
        stage('Build and Test') { // Renamed the stage for clarity
            steps {
                script {
                    sh """#!/bin/bash -ex
                        # Create a virtual environment
                        python3 -m venv venv

                        # Activate the environment in the same shell
                        source venv/bin/activate

                        # Install dependencies using the virtual environment's pip
                        python3 -m pip install -r requirements.txt

                        # Run your tests using the virtual environment's python
                        # IMPORTANT: Generate a JUnit XML report for Jenkins
                        sh "pytest src/tests --alluredir=allure-results --junitxml=test-results/junit_report.xml --browser chrome-headless --base-url ${params.STAGING_URL_PARAM}"
                    """
                }
            }
        }
         stage('Generate Allure Report') {
            steps {
                script {
                    // Assuming Allure Commandline tool is installed on your Jenkins agent
                    // If not, you might need a 'tool' directive or download it
                    sh "allure generate allure-results --clean -o allure-report"
                }
            }
        }
    }
    // This 'post' section will execute after the 'stages' section completes
    post {
        always {
           
            junit '**/test-results.xml'

        }
    }
}