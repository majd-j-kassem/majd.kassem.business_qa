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
                // The 'node' step is important for specifying where this part of the pipeline runs.
                // Ensure you have a Jenkins agent (like your Built-in Node) with the label 'jenkins'.
                // If not, change 'jenkins' to 'master' or 'any' or the label of your agent.
                node('jenkins') {
                    checkout scm // Ensure the workspace is clean for this stage

                    // Use withEnv to set BASE_URL for the duration of this block
                    withEnv(["BASE_URL=${RENDER_DEV_URL}"]) {
                        script {
                            echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                            // --- IMPORTANT PERMISSION FIXES ---
                            // 1. Create directories on the Jenkins host's workspace
                            //    These directories will be mounted into the Docker container.
                            sh 'mkdir -p test-results allure-results'

                            // 2. Set permissions for these directories ON THE JENKINS HOST.
                            //    'chmod 777' is broad but ensures the user in the container
                            //    can write to these mounted volumes.
                            // FIX: Added 'chmod -R 777' back here. You had removed the 'chmod -R 777' command.
                            sh 'chmod -R 777 test-results allure-results'


                            // Now, run pytest inside the Docker container
                            // Use the FULL_DOCKER_IMAGE_NAME that was built earlier
                            docker.image(env.FULL_DOCKER_IMAGE_NAME).inside {
                                // IMPORTANT: Inside the container, also ensure permissions on the mounted paths.
                                // This is a belt-and-suspenders approach to permission issues.
                                // FIX: Added 'chmod -R 777' back here for the allure-results and test-results paths.
                                // It seems necessary due to the way docker handles UIDs/GIDs and volume mounts.
                                sh "chmod -R 777 ${ALLURE_RESULTS_PATH_IN_CONTAINER}"
                                sh "chmod -R 777 /home/seluser/test-results" // Ensure JUnit path is also writable

                                // Run pytest.
                                // Paths here are as seen from INSIDE the Docker container.
                                sh "pytest src/tests --browser chrome-headless --base-url ${env.BASE_URL} --junitxml=${JUNIT_REPORT_FILE} --alluredir=${ALLURE_RESULTS_PATH_IN_CONTAINER}"
                            }
                        }
                    }
                }
            }
            post {
                always {
                    // This runs on the Jenkins agent (host), so the path should be relative to its workspace.
                    junit 'test-results/junit-report.xml'
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
                    sh "rm -rf test-results allure-results" // Relative paths to workspace
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