pipeline {
    agent {
        // Use a Docker agent to ensure a consistent environment for your tests.
        // This image should have Python, Pip, Chrome, and ChromeDriver installed.
        // You might need to build your own custom Docker image if a standard one doesn't suffice.
        docker {
            image 'selenium/standalone-chrome:latest' // Or a more specific version, or your custom image
            args '-v /dev/shm:/dev/shm' // Required for Chrome in Docker to prevent crashing
        }
    }

    environment {
        // Define your Render URLs as environment variables
        RENDER_DEV_URL = 'https://majd-kassem-business-dev.onrender.com/' // Replace with your actual Dev URL
        RENDER_PROD_URL = 'https://majd-kassem-business.onrender.com/' // Replace with your actual Prod URL
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    // Ensure the workspace is clean before cloning
                    // deleteDir() // Uncomment if you want a completely clean workspace every time
                    git branch: 'main', url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git' // Replace with your actual GitHub URL and branch
                    sh 'ls -la' // Just to verify files are checked out
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Assuming Python is already in the selenium/standalone-chrome image or you're adding it
                    sh 'pip install --upgrade pip'
                    sh 'pip install -r requirements.txt' // Ensure you have a requirements.txt file
                    sh 'pip install pytest' // Install pytest if not in requirements.txt
                }
            }
        }

        stage('Run Tests - Render Dev') {
            steps {
                script {
                    // Run tests against the Dev Render URL in headless mode
                    sh "pytest src/tests --browser chrome-headless --base-url ${RENDER_DEV_URL}"
                }
            }
            post {
                // Actions to take after this stage completes
                always {
                    // Publish JUnit test results if you configure pytest to output them
                    // Example: pytest --junitxml=results.xml
                    // junit 'results.xml'
                }
                failure {
                    echo "Tests against Render Dev failed!"
                }
            }
        }

        stage('Run Tests - Render Prod') {
            steps {
                script {
                    // Run tests against the Prod Render URL in headless mode
                    // This stage will only run if the previous stage (Dev tests) passed
                    sh "pytest src/tests --browser chrome-headless --base-url ${RENDER_PROD_URL}"
                }
            }
            post {
                always {
                    // junit 'results.xml' // Again, if you're outputting JUnit results
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
                    // Clean up any generated files, though the Docker agent usually cleans itself
                    // deleteDir() // Uncomment with caution, removes the entire workspace
                }
            }
        }
    }

    post {
        // Actions to take after the entire pipeline completes
        always {
            echo "Pipeline finished."
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