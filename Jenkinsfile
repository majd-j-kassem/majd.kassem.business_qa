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
        RENDER_LIVE_SERVICE_ID = 'srv-d0h686q4d50c73c6g410' // This is now correctly set

        // --- IMPORTANT: Jenkins Credential ID for Render API Key ---
        // This MUST match the ID you gave your Secret text credential in Jenkins.
        RENDER_API_KEY_CREDENTIAL_ID = 'render-api-key'

        // --- Consistent path for your JUnit XML report ---
        // This path is relative to the workspace INSIDE the Docker container.
        JUNIT_REPORT_FILE = 'test-results/junit-report.xml'

        // --- Consistent path for Allure raw data inside the Docker container's mounted workspace ---
        // NEW ENVIRONMENT VARIABLE FOR ALLURE RESULTS
        ALLURE_RESULTS_PATH_IN_CONTAINER = "/home/seluser/allure-results" 

        // --- Name for your custom Docker image ---
        CUSTOM_DOCKER_IMAGE_NAME = 'majd-selenium-runner'

        // --- Full Docker image name including tag, derived from BUILD_NUMBER ---
        FULL_DOCKER_IMAGE_NAME = "${CUSTOM_DOCKER_IMAGE_NAME}:${BUILD_NUMBER}"
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
                    echo "Building custom Docker image: ${env.FULL_DOCKER_IMAGE_NAME}"
                    // Build the Docker image. It will be automatically tagged with FULL_DOCKER_IMAGE_NAME
                    docker.build(env.FULL_DOCKER_IMAGE_NAME, ".")
                    echo "Custom Docker Image built: ${env.FULL_DOCKER_IMAGE_NAME}"
                }
            }
        }

        stage('Run Tests - Render Dev (CI Phase)') {
                steps {
                    node('jenkins') { // Assuming your pipeline agent is named 'jenkins'
                        checkout scm
                        withEnv(["BASE_URL=https://majd-kassem-business-dev.onrender.com/"]) {
                            script {
                                echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                                // Create the test-results directory
                                sh 'mkdir -p /var/lib/jenkins/workspace/y-app-dev-deploy-and-tes@2/test-results'

                                // Create the allure-results directory
                                sh 'mkdir -p /var/lib/jenkins/workspace/y-app-dev-deploy-and-tes@2/allure-results'

                                // Set permissions for allure-results
                                // This assumes the Jenkins user (jenkins) is the one needing write access.
                                // If the docker container's user (seluser) needs access,
                                // the chmod should ideally happen *inside* the docker container or
                                // you need to manage volume permissions more carefully.
                                // Given your previous error, let's try making it world-writable for now
                                // until we confirm the user context inside the container.
                                sh 'chmod -R 777 /var/lib/jenkins/workspace/y-app-dev-deploy-and-tes@2/allure-results'

                                // Now run pytest inside the Docker container
                                docker.image('majd-selenium-runner:22').inside {
                                    // The `pytest` command is what you had before.
                                    // Note that the paths within the container are `/home/seluser/test-results`
                                    // and `/home/seluser/allure-results` due to the volume mappings.
                                    sh 'pytest src/tests --browser chrome-headless --base-url https://majd-kassem-business-dev.onrender.com/ --junitxml=test-results/junit-report.xml --alluredir=/home/seluser/allure-results'
                                }
                            }
                        }
                    }
                }
                post {
                    always {
                        junit 'test-results/junit-report.xml' // Ensure this path is correct
                    }
                    failure {
                        echo "Tests against Render Dev FAILED! Build will stop here. ❌"
                    }
                }
            }
        stage('Deploy to Render Live (CD Phase)') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
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
                    // Remove the generated report files from the host workspace
                    sh "rm -rf ${WORKSPACE}/test-results ${WORKSPACE}/allure-results ${WORKSPACE}/allure-report"
                    // Remove the custom Docker image to save space
                    sh "docker rmi -f ${env.FULL_DOCKER_IMAGE_NAME}"
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