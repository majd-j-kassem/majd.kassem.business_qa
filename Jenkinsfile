// Jenkinsfile (Declarative Pipeline)

pipeline {
    agent {
        docker {
            image 'selenium/standalone-chrome:latest'
            args '-v /dev/shm:/dev/shm'
        }
    }

    environment {
        RENDER_DEV_URL = 'https://majd-kassem-business-dev.onrender.com/'
        RENDER_PROD_URL = 'https://majd-kassem-business.onrender.com/'
        // Define paths for JUnit reports
        DEV_JUNIT_REPORT = "target/junit-dev-results.xml"
        PROD_JUNIT_REPORT = "target/junit-prod-results.xml"
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    git branch: 'main', url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git'
                    sh 'ls -la'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'pip install --upgrade pip --user' // Add --user here too
                    sh 'pip install -r requirements.txt --user' // <--- ADDED --user HERE
                    sh 'pip install pytest --user' // <--- ADDED --user HERE (if you keep this line)
                    echo "Python test dependencies installed."
                }
            }
        }

        stage('Run Tests - Render Dev') {
            steps {
                script {
                    // Run tests against the Dev Render URL in headless mode, outputting JUnit XML
                    sh "pytest src/tests --browser chrome-headless --base-url ${RENDER_DEV_URL} --junitxml=${DEV_JUNIT_REPORT}"
                }
            }
            post {
                always {
                    // Publish JUnit test results for Dev stage
                    junit testResults: "${DEV_JUNIT_REPORT}", allowEmptyResults: true
                }
                failure {
                    echo "Tests against Render Dev failed!"
                }
            }
        }

        stage('Run Tests - Render Prod') {
            steps {
                script {
                    // Run tests against the Prod Render URL in headless mode, outputting JUnit XML
                    sh "pytest src/tests --browser chrome-headless --base-url ${RENDER_PROD_URL} --junitxml=${PROD_JUNIT_REPORT}"
                }
            }
            post {
                always {
                    // Publish JUnit test results for Prod stage
                    junit testResults: "${PROD_JUNIT_REPORT}", allowEmptyResults: true
                }
                failure {
                    echo "Tests against Render Prod failed!"
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    sh 'echo "Cleaning up workspace..."'
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished."
            cleanWs() // Clean the Jenkins workspace
        }
        success {
            echo "All tests passed successfully!"
        }
        failure {
            echo "Some tests failed!"
        }
        aborted {
            echo "Pipeline was aborted."
        }
    }
}