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

        // --- Simplified internal paths for reports ---
        // These paths will now be relative to the Jenkins workspace on the host,
        // which is mounted to the same path as inside the container.
        JUNIT_REPORT_FILE_INTERNAL = 'test-results/junit-report.xml'
        ALLURE_RESULTS_PATH_INTERNAL = 'allure-results'

        // --- Name for your custom Docker image ---
        CUSTOM_DOCKER_IMAGE_NAME = 'majd-selenium-runner'

        // --- Full Docker image name including tag, derived from BUILD_NUMBER ---
        FULL_DOCKER_IMAGE_NAME = "${CUSTOM_DOCKER_IMAGE_NAME}:${BUILD_NUMBER}"

        // --- Allure Commandline Tool Name ---
        // This MUST match the name you configured under Jenkins > Manage Jenkins > Tools > Allure Commandline installations
        ALLURE_COMMANDLINE_TOOL_NAME = 'Allure_2.27.0' // Make sure this matches your configuration
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
                // Using 'node('jenkins')' ensures the test execution happens on a Jenkins agent,
                // which is good practice for Docker operations.
                node('jenkins') {
                    // Re-checkout SCM here if you need a fresh workspace for this stage,
                    // or if this stage runs on a different agent.
                    // For now, removing to avoid redundant checkout if 'agent any' is sufficient.
                    // If you face issues with file availability, re-add 'checkout scm' here.
                    // checkout scm // Uncomment if needed

                    withEnv(["BASE_URL=${RENDER_DEV_URL}"]) {
                        script {
                            echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                            // --- IMPORTANT: Create directories on the Jenkins host's workspace ---
                            // These directories will be mounted into the Docker container.
                            sh "mkdir -p test-results allure-results"
                            // Set permissions for these directories ON THE JENKINS HOST.
                            // This ensures the container user can write to them.
                            sh "chmod -R 777 test-results allure-results"

                            // Now, run pytest inside the Docker container
                            docker.image(env.FULL_DOCKER_IMAGE_NAME).inside {
                                echo "--- Inside Docker Container (Before Pytest) ---"
                                sh 'pwd' // Should show the Jenkins workspace path inside the container
                                sh 'ls -la'
                                sh 'ls -la test-results'
                                sh 'ls -la allure-results'
                                echo "Attempting to run pytest..."

                                // Pytest command will write to the mounted volumes:
                                // ${WORKSPACE}/test-results/junit-report.xml
                                // ${WORKSPACE}/allure-results
                                // Using ${WORKSPACE} here is crucial as it refers to the mounted Jenkins workspace
                                // path inside the container, ensuring reports are written to the host.
                                def pytestCommand = "pytest src/tests --browser chrome-headless --base-url ${env.BASE_URL} --junitxml=${WORKSPACE}/${env.JUNIT_REPORT_FILE_INTERNAL} --alluredir=${WORKSPACE}/${env.ALLURE_RESULTS_PATH_INTERNAL}"
                                def pytestExitCode = sh(script: pytestCommand, returnStatus: true)

                                echo "Pytest command finished with exit code: ${pytestExitCode}"

                                echo "--- Inside Docker Container (After Pytest) ---"
                                sh "ls -la test-results"
                                sh "ls -la allure-results"

                                // --- REPORT PUBLISHING (MOVED INSIDE CONTAINER BLOCK) ---
                                // These steps now run while still inside the Docker container,
                                // ensuring access to the newly generated report files.

                                // JUnit Report Publishing
                                if (fileExists("${WORKSPACE}/${env.JUNIT_REPORT_FILE_INTERNAL}")) {
                                    echo "Found JUnit report file: ${env.JUNIT_REPORT_FILE_INTERNAL}. Publishing results."
                                    junit "${WORKSPACE}/${env.JUNIT_REPORT_FILE_INTERNAL}"
                                } else {
                                    echo "WARNING: JUnit report file not found at ${env.JUNIT_REPORT_FILE_INTERNAL}. Skipping JUnit publishing."
                                }

                                // Allure Report Publishing
                                // Check if the allure-results directory exists and is not empty
                                if (fileExists("${WORKSPACE}/${env.ALLURE_RESULTS_PATH_INTERNAL}")) {
                                    // Count files/directories within allure-results to check if it's empty
                                    // Use 'ls -A' to include dotfiles (like .json, .txt) which Allure generates
                                    def fileCount = sh(script: "ls -A ${WORKSPACE}/${env.ALLURE_RESULTS_PATH_INTERNAL} | wc -l", returnStdout: true).trim() as int

                                    if (fileCount > 0) {
                                        echo "Found Allure results in ${env.ALLURE_RESULTS_PATH_INTERNAL}. Publishing Allure Report."
                                        // The 'allure' step will use the specified tool and results path
                                        withEnv(["PATH+ALLURE=${tool env.ALLURE_COMMANDLINE_TOOL_NAME}/bin"]) { // Add Allure to PATH
                                            allure([
                                                reportBuildPolicy: 'ALWAYS', // Generates report even if previous fails
                                                results: [[path: "${WORKSPACE}/${env.ALLURE_RESULTS_PATH_INTERNAL}"]]
                                            ])
                                        }
                                        echo "Allure Report publishing complete."
                                    } else {
                                        echo "WARNING: Allure results directory found but empty at ${env.ALLURE_RESULTS_PATH_INTERNAL}. Skipping Allure Report publishing."
                                    }
                                } else {
                                    echo "WARNING: Allure results directory not found at ${env.ALLURE_RESULTS_PATH_INTERNAL}. Skipping Allure Report publishing."
                                }
                                // END OF REPORT PUBLISHING

                                // Fail the build if pytest didn't exit cleanly
                                if (pytestExitCode != 0) {
                                    error "Pytest tests failed (exit code: ${pytestExitCode}). Check logs above for details."
                                }
                            } // End of docker.image().inside {}
                        } // End of script block inside withEnv
                    } // End of withEnv
                } // End of node('jenkins')
            } // End of steps
            // Removed the post block from inside the stage, as reporting is now handled within steps
        }

        stage('Deploy to Render Live (CD Phase)') {
            when {
                // Only run this stage if the previous stages (especially tests) were successful
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "Tests passed. Triggering deployment of the System Under Test to Render Live..."
                    // Use withCredentials to securely inject the API key
                    withCredentials([string(credentialsId: env.RENDER_API_KEY_CREDENTIAL_ID, variable: 'RENDER_API_KEY')]) {
                        // Using double quotes for the entire curl command and escaping internal quotes
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
                    // These are relative to the Jenkins workspace
                    sh "rm -rf test-results allure-results"
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