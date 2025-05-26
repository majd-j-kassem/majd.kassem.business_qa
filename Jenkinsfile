pipeline {
    // We use 'agent any' at the top level because we'll build our custom Docker image
    // in a specific stage and then use that image in subsequent stages.
    agent any

    environment {
        // --- Render Service URLs ---
        RENDER_DEV_URL = 'https://majd-kassem-business-dev.onrender.com/'
        RENDER_PROD_URL = 'https://majd-kassem-business.onrender.com/'

        // --- IMPORTANT: Render Live Service ID ---
        // Get this from your Render Dashboard URL for your Live service (e.g., srv-xxxxxxxxxxxxxxxxx)
        RENDER_LIVE_SERVICE_ID = 'srv-your-render-live-service-id-here' // <<-- REPLACE THIS!

        // --- IMPORTANT: Jenkins Credential ID for Render API Key ---
        // This MUST match the ID you gave your Secret text credential in Jenkins.
        RENDER_API_KEY_CREDENTIAL_ID = 'render-api-key' // <<-- ENSURE THIS MATCHES YOUR JENKINS CREDENTIAL ID

        // --- Consistent path for your JUnit XML report ---
        // This path is relative to the workspace INSIDE the Docker container.
        JUNIT_REPORT_FILE = 'test-results/junit-report.xml'

        // --- Name for your custom Docker image ---
        CUSTOM_DOCKER_IMAGE_NAME = 'majd-selenium-runner'
    }

    stages {
        stage('Checkout Selenium Test Code') {
            steps {
                script {
                    // This checks out your Selenium test automation project from GitHub
                    git branch: 'dev', url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git'
                    sh 'ls -la' // List files to verify checkout
                    echo "Selenium test code checked out."
                }
            }
        }

        stage('Build Custom Test Image') {
            steps {
                script {
                    echo "Building custom Docker image: ${env.CUSTOM_DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    // Build the Docker image from the Dockerfile in the current workspace ('.')
                    // This image will now include all your Python dependencies
                    dockerImage = docker.build("${env.CUSTOM_DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    echo "Custom Docker Image built: ${dockerImage.id}"
                }
            }
        }

        stage('Run Tests - Render Dev (CI Phase)') {
            steps {
                script {
                    // Use the custom Docker image for this stage
                    dockerImage.run("""-v /dev/shm:/dev/shm -v ${WORKSPACE}/test-results:/home/seluser/test-results""") {
                        echo "Running tests against Render Dev: ${env.RENDER_DEV_URL} inside custom Docker image."
                        // Create directory for JUnit report inside the container
                        sh "mkdir -p test-results"
                        // Run pytest. Dependencies are now pre-installed in the image.
                        sh "pytest src/tests --browser chrome-headless --base-url ${env.RENDER_DEV_URL} --junitxml=${env.JUNIT_REPORT_FILE}"
                    }
                }
            }
            post {
                always {
                    // Publish JUnit test results for this stage in Jenkins UI
                    // The report file is mounted back to the host workspace, so Jenkins can find it.
                    junit "${WORKSPACE}/test-results/junit-report.xml"
                }
                failure {
                    echo "Tests against Render Dev FAILED! Build will stop here. ❌"
                }
                success {
                    echo "Tests against Render Dev PASSED! Proceeding to potential deployment. ✅"
                }
            }
        }

        stage('Deploy to Render Live (CD Phase)') {
            // This stage will only run if the 'Run Tests - Render Dev' stage passed successfully.
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    // This stage does NOT need the custom Docker image, as it's just a curl command.
                    // It runs on the Jenkins agent itself.
                    echo "Tests passed. Triggering deployment of the System Under Test to Render Live..."
                    withCredentials([string(credentialsId: env.RENDER_API_KEY_CREDENTIAL_ID, variable: 'RENDER_API_KEY')]) {
                        sh "curl -X POST -H \"Authorization: Bearer ${RENDER_API_KEY}\" \"https://api.render.com/v1/services/${env.RENDER_LIVE_SERVICE_ID}/deploys\""
                    }
                    echo "Deployment trigger sent to Render Live! Check Render dashboard for status."
                }
            }
            post {
                failure {
                    echo "Failed to trigger Render Live deployment! Please check API key, Service ID, or Render status. ❌"
                }
                success {
                    echo "Successfully triggered Render Live deployment. 🎉"
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up workspace and removing custom Docker image..."
                    // Remove the generated JUnit report file from the host workspace
                    sh "rm -f ${WORKSPACE}/test-results/junit-report.xml"
                    // Remove the custom Docker image to save space
                    sh "docker rmi -f ${env.CUSTOM_DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                }
            }
        }
    }

    post {
        // Global actions after the entire pipeline finishes
        always {
            echo "Pipeline finished for job ${env.JOB_NAME}, build number ${env.BUILD_NUMBER}."
        }
        success {
            echo "Overall pipeline SUCCESS: All tests passed and Render Live deployment triggered. 🎉"
        }
        failure {
            echo "Overall pipeline FAILED: Some tests did not pass or deployment failed. ❌"
        }
        aborted {
            echo "Overall pipeline ABORTED: Build was manually stopped. 🚫"
        }
    }
}