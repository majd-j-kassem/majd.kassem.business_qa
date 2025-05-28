pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Create a virtual environment (optional but recommended)
                script {
                    sh "python3 -m venv venv"  // Or "python -m venv venv" for Python 2
                    sh "source venv/bin/activate" // Activate the environment
                    sh "python3 -m pip install -r requirements.txt" // Install dependencies
                    sh "python3 pytest src/tests/ --browser chrome" // Run your Python script
                    // Add more steps here, like running tests or packaging
                }
            }
        }
    }
}