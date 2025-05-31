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
                        python3 -m pytest --junitxml=test-results.xml src/tests/ --browser chrome-headless
                    """
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