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

     stage('Run Tests - Render Dev (CI Phase)') {
            steps {
                node('jenkins') {
                    checkout scm

                    withEnv(["BASE_URL=${RENDER_DEV_URL}"]) {
                        script {
                            echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                            // 1. Create directories on the Jenkins host's workspace
                            sh 'mkdir -p test-results allure-results'

                            // 2. Set permissions for these directories ON THE JENKINS HOST.
                            sh 'chmod -R 777 test-results allure-results'

                            // Now, run pytest inside the Docker container
                            docker.image(env.FULL_DOCKER_IMAGE_NAME).inside {
                                // IMPORTANT: Inside the container, also ensure permissions on the mounted paths.
                                sh "chmod -R 777 ${ALLURE_RESULTS_PATH_IN_CONTAINER}"
                                sh "chmod -R 777 /home/seluser/test-results"

                                // --- ADD DEBUGGING COMMANDS HERE ---
                                echo "--- Inside Docker Container (Before Pytest) ---"
                                sh 'pwd' // Show current working directory inside container
                                sh 'ls -la' // List contents of current working directory
                                sh 'ls -la test-results' // Check if test-results directory exists and permissions
                                sh 'ls -la allure-results' // Check if allure-results directory exists and permissions
                                echo "Attempting to run pytest..."

                                // Run pytest.
                                // Capture the exit code of pytest
                                def pytestExitCode = sh(script: "pytest src/tests --browser chrome-headless --base-url ${env.BASE_URL} --junitxml=${JUNIT_REPORT_FILE} --alluredir=${ALLURE_RESULTS_PATH_IN_CONTAINER}", returnStatus: true)

                                echo "Pytest command finished with exit code: ${pytestExitCode}"

                                echo "--- Inside Docker Container (After Pytest) ---"
                                sh 'ls -la test-results' // Check if junit-report.xml was created
                                sh 'ls -la allure-results' // Check if allure files were created

                                // If pytest failed, ensure the pipeline fails immediately.
                                if (pytestExitCode != 0) {
                                    error "Pytest tests failed (exit code: ${pytestExitCode})."
                                }
                            }
                        }
                    }
                }
            }
            post {
                always {
                    // Check if the report file exists on the host before trying to publish.
                    script {
                        def junitReportPath = "test-results/junit-report.xml"
                        if (fileExists(junitReportPath)) {
                            echo "Found JUnit report file: ${junitReportPath}. Publishing results."
                            junit junitReportPath
                        } else {
                            echo "WARNING: JUnit report file not found at ${junitReportPath}. Skipping JUnit publishing."
                            // Optionally, fail the build here if you absolutely require a report
                            // error "JUnit report not found. Build will fail."
                        }
                    }
                }
                failure {
                    echo "Tests against Render Dev FAILED! Build will stop here. ❌"
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