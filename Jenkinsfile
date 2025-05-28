pipeline {
    agent any
    stages {
        stage('Build') {
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
                        python3 -m pytest src/tests
                    """
                }
            }
        }
    }
}